import os
import re
import unicodedata
import warnings
from time import gmtime, localtime, strftime, time

from django.conf import settings as dj_settings
from django.core.files.storage import default_storage

from filebrowser_safe import settings as fb_settings

try:
    from mezzanine.utils.sites import current_site_id
except ImportError:
    # TODO: filebrowser-safe should not rely on `current_site_id` at all since its
    # provided by Mezzanine.
    #
    # For now we just want to be able tu run the test suite without having mezzanine
    # installed, and this will do. Remove once filebrowser-safe is completely decoupled
    # from mezzanine.
    warnings.warn(
        """
        You are using a placeholder implementation of the current_site_id function
        intended for test purposes only. If you're seeing this you might have a problem
        with your Mezzanine installation.
        """
    )

    def current_site_id():
        return dj_settings.SITE_ID


def get_directory():
    """
    Returns FB's ``DIRECTORY`` setting, appending a directory using
    the site's ID if ``MEDIA_LIBRARY_PER_SITE`` is ``True``, and also
    creating the root directory if missing.
    """

    dirname = fb_settings.DIRECTORY
    if getattr(dj_settings, "MEDIA_LIBRARY_PER_SITE", False):
        dirname = os.path.join(dirname, "site-%s" % current_site_id())
    fullpath = os.path.join(dj_settings.MEDIA_ROOT, dirname)
    if not default_storage.isdir(fullpath):
        default_storage.makedirs(fullpath)
    return dirname


def path_strip(path, root):
    if not path or not root:
        return path
    path = os.path.normcase(path)
    root = os.path.normcase(root)
    if path.startswith(root):
        return path[len(root) :]
    return path


def path_to_url(value):
    """
    Change PATH to URL.
    Value has to be a PATH relative to MEDIA_ROOT.

    Return an URL relative to MEDIA_ROOT.
    """
    mediaroot_re = re.compile(r"^(%s)" % (fb_settings.MEDIA_ROOT))
    value = mediaroot_re.sub("", value)
    return url_join(fb_settings.MEDIA_URL, value)


def dir_from_url(value):
    """
    Get the relative server directory from a URL.
    URL has to be an absolute URL including MEDIA_URL or
    an URL relative to MEDIA_URL.
    """
    mediaurl_re = re.compile(r"^(%s)" % (fb_settings.MEDIA_URL))
    value = mediaurl_re.sub("", value)
    directory_re = re.compile(r"^(%s)" % (get_directory()))
    value = directory_re.sub("", value)
    return os.path.split(value)[0]


def url_join(*args):
    """
    URL join routine.
    """
    if args[0].startswith("http://"):
        url = "http://"
    else:
        url = "/"
    for arg in args:
        arg = str(arg).replace("\\", "/")
        arg_split = arg.split("/")
        for elem in arg_split:
            if elem != "" and elem != "http:":
                url = url + elem + "/"
    # remove trailing slash for filenames
    if os.path.splitext(args[-1])[1]:
        url = url.rstrip("/")
    return url


def get_path(path):
    """
    Get Path.
    """
    if (
        path.startswith(".")
        or "../" in path
        or os.path.isabs(path)
        or not default_storage.isdir(os.path.join(get_directory(), path))
    ):
        return None
    return path


def get_file(path, filename):
    """
    Get File.
    """
    if not default_storage.exists(os.path.join(get_directory(), path, filename)):
        return None
    return filename


def get_breadcrumbs(query, path):
    """
    Get breadcrumbs.
    """
    breadcrumbs = []
    dir_query = ""
    if path:
        for item in path.split(os.sep):
            dir_query = os.path.join(dir_query, item)
            breadcrumbs.append([item, dir_query])
    return breadcrumbs


def get_filterdate(filterDate, dateTime):
    """
    Get filterdate.
    """
    returnvalue = ""
    dateYear = strftime("%Y", gmtime(dateTime))
    dateMonth = strftime("%m", gmtime(dateTime))
    dateDay = strftime("%d", gmtime(dateTime))
    if (
        filterDate == "today"
        and int(dateYear) == int(localtime()[0])
        and int(dateMonth) == int(localtime()[1])
        and int(dateDay) == int(localtime()[2])
    ):
        returnvalue = "true"
    elif filterDate == "thismonth" and dateTime >= time() - 2592000:
        returnvalue = "true"
    elif filterDate == "thisyear" and int(dateYear) == int(localtime()[0]):
        returnvalue = "true"
    elif filterDate == "past7days" and dateTime >= time() - 604800:
        returnvalue = "true"
    elif filterDate == "":
        returnvalue = "true"
    return returnvalue


def get_settings_var():
    """
    Get settings variables used for FileBrowser listing.
    """
    settings_var = {}
    # Main
    settings_var["DEBUG"] = fb_settings.DEBUG
    settings_var["MEDIA_ROOT"] = fb_settings.MEDIA_ROOT
    settings_var["MEDIA_URL"] = fb_settings.MEDIA_URL
    settings_var["DIRECTORY"] = get_directory()
    # FileBrowser
    settings_var["PATH_FILEBROWSER_MEDIA"] = fb_settings.PATH_FILEBROWSER_MEDIA
    # TinyMCE
    settings_var["URL_TINYMCE"] = fb_settings.URL_TINYMCE
    settings_var["PATH_TINYMCE"] = fb_settings.PATH_TINYMCE
    # Extensions/Formats (for FileBrowseField)
    settings_var["EXTENSIONS"] = fb_settings.EXTENSIONS
    settings_var["SELECT_FORMATS"] = fb_settings.SELECT_FORMATS
    # FileBrowser Options
    settings_var["MAX_UPLOAD_SIZE"] = fb_settings.MAX_UPLOAD_SIZE
    # Convert Filenames
    settings_var["CONVERT_FILENAME"] = fb_settings.CONVERT_FILENAME
    return settings_var


def get_file_type(filename):
    """
    Get file type as defined in EXTENSIONS.
    """
    file_extension = os.path.splitext(filename)[1].lower()
    file_type = ""
    for k, v in fb_settings.EXTENSIONS.items():
        for extension in v:
            if file_extension == extension.lower():
                file_type = k
    return file_type


def is_selectable(filename, selecttype):
    """
    Get select type as defined in FORMATS.
    """
    file_extension = os.path.splitext(filename)[1].lower()
    select_types = []
    for k, v in fb_settings.SELECT_FORMATS.items():
        for extension in v:
            if file_extension == extension.lower():
                select_types.append(k)
    return select_types


def convert_filename(value):
    """
    Convert Filename.
    https://github.com/sehmaschine/django-filebrowser/blob/master/filebrowser/functions.py
    """

    if fb_settings.NORMALIZE_FILENAME:
        chunks = value.split(os.extsep)
        normalized = []

        for v in chunks:
            v = (
                unicodedata.normalize("NFKD", str(v))
                .encode("ascii", "ignore")
                .decode("ascii")
            )
            v = re.sub(r"[^\w\s-]", "", v).strip()
            normalized.append(v)

        if len(normalized) > 1:
            value = ".".join(normalized)
        else:
            value = normalized[0]

    if fb_settings.CONVERT_FILENAME:
        value = value.replace(" ", "_").lower()

    return value
