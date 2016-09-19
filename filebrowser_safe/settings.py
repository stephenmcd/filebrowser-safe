from __future__ import unicode_literals
# coding: utf-8

# imports
import os

# django imports
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# settings for django-tinymce
try:
    import tinymce.settings
    DEFAULT_URL_TINYMCE = tinymce.settings.JS_BASE_URL + '/'
    DEFAULT_PATH_TINYMCE = tinymce.settings.JS_ROOT + '/'
except ImportError:
    DEFAULT_URL_TINYMCE = settings.STATIC_URL + "grappelli/tinymce/jscripts/tiny_mce/"
    DEFAULT_PATH_TINYMCE = os.path.join(settings.MEDIA_ROOT, 'admin/tinymce/jscripts/tiny_mce/')

# Set to True in order to see the FileObject when Browsing.
DEBUG = getattr(settings, "FILEBROWSER_DEBUG", False)

# Main Media Settings
MEDIA_ROOT = getattr(settings, "FILEBROWSER_MEDIA_ROOT", settings.MEDIA_ROOT)
MEDIA_URL = getattr(settings, "FILEBROWSER_MEDIA_URL", settings.MEDIA_URL)

# Main FileBrowser Directory. This has to be a directory within MEDIA_ROOT.
# Leave empty in order to browse all files under MEDIA_ROOT.
# DO NOT USE A SLASH AT THE BEGINNING, DO NOT FORGET THE TRAILING SLASH AT THE END.
DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')

# The URL/PATH to your filebrowser media-files.
URL_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_URL_FILEBROWSER_MEDIA", "%sfilebrowser/" % settings.STATIC_URL)
PATH_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_PATH_FILEBROWSER_MEDIA", os.path.join(settings.MEDIA_ROOT, 'filebrowser/'))

# The URL/PATH to your TinyMCE Installation.
URL_TINYMCE = getattr(settings, "FILEBROWSER_URL_TINYMCE", DEFAULT_URL_TINYMCE)
PATH_TINYMCE = getattr(settings, "FILEBROWSER_PATH_TINYMCE", DEFAULT_PATH_TINYMCE)

# Allowed Extensions for File Upload. Lower case is important.
# Please be aware that there are Icons for the default extension settings.
# Therefore, if you add a category (e.g. "Misc"), you won't get an icon.
EXTENSIONS = {
    'Folder': [''],
    'Image': ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff', '.svg'],
    'Video': ['.mov', '.wmv', '.mpeg', '.mpg', '.avi', '.rm', '.mp4'],
    'Document': ['.pdf', '.doc', '.rtf', '.txt', '.xls', '.csv', '.docx'],
    'Audio': ['.mp3', '.wav', '.aiff', '.midi', '.m4p'],
    'Code': ['.html', '.py', '.js', '.css']
}
EXTENSIONS.update(getattr(settings, "FILEBROWSER_EXTENSIONS", {}))

ESCAPED_EXTENSIONS = getattr(settings, 'FILEBROWSER_ESCAPED_EXTENSIONS', ('html', 'svg'))

# Define different formats for allowed selections.
# This has to be a subset of EXTENSIONS.
SELECT_FORMATS = {
    'File': ['Folder', 'Document'],
    'Image': ['Image'],
    'Media': ['Video', 'Audio'],
    'Document': ['Document'],
    # for TinyMCE we can also define lower-case items
    'image': ['Image'],
    'file': ['Folder', 'Image', 'Document'],
    'media': ['Video', 'Audio'],
}
SELECT_FORMATS.update(getattr(settings, "FILEBROWSER_SELECT_FORMATS", {}))

# EXTRA SETTINGS
# True to save the URL including STATIC_URL to your model fields
# or False (default) to save path relative to STATIC_URL.
# Note: Full URL does not necessarily means absolute URL.
SAVE_FULL_URL = getattr(settings, "FILEBROWSER_SAVE_FULL_URL", True)
# If set to True, the FileBrowser will not try to import a mis-installed PIL.
STRICT_PIL = getattr(settings, 'FILEBROWSER_STRICT_PIL', False)
# PIL's Error "Suspension not allowed here" work around:
# s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
IMAGE_MAXBLOCK = getattr(settings, 'FILEBROWSER_IMAGE_MAXBLOCK', 1024 * 1024)
# Exclude files matching any of the following regular expressions
# Default is to exclude 'thumbnail' style naming of image-thumbnails.
EXTENSION_LIST = []
for exts in list(EXTENSIONS.values()):
    EXTENSION_LIST += exts
EXCLUDE = getattr(settings, 'FILEBROWSER_EXCLUDE', (r'_(%(exts)s)_.*_q\d{1,3}\.(%(exts)s)' % {'exts': ('|'.join(EXTENSION_LIST))},))
# Max. Upload Size in Bytes.
MAX_UPLOAD_SIZE = getattr(
    settings,
    "FILEBROWSER_MAX_UPLOAD_SIZE",
    settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
# Normalize filename and remove all non-alphanumeric characters
# except for underscores, spaces & dashes.
NORMALIZE_FILENAME = getattr(settings, "FILEBROWSER_NORMALIZE_FILENAME", False)
# Convert Filename (replace spaces and convert to lowercase)
CONVERT_FILENAME = getattr(settings, "FILEBROWSER_CONVERT_FILENAME", True)
# Max. Entries per Page
# Loading a Sever-Directory with lots of files might take a while
# Use this setting to limit the items shown
LIST_PER_PAGE = getattr(settings, "FILEBROWSER_LIST_PER_PAGE", 50)
# Default Sorting
# Options: date, filesize, filename_lower, filetype_checked
DEFAULT_SORTING_BY = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_BY", "date")
# Sorting Order: asc, desc
DEFAULT_SORTING_ORDER = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_ORDER", "desc")
# regex to clean dir names before creation
FOLDER_REGEX = getattr(settings, "FILEBROWSER_FOLDER_REGEX", r'^[\sa-zA-Z0-9_/-]+$')

# EXTRA TRANSLATION STRINGS
# The following strings are not availabe within views or templates
_('Folder')
_('Image')
_('Video')
_('Document')
_('Audio')
_('Code')
