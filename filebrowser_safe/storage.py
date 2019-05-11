from __future__ import unicode_literals
# coding: utf-8

# PYTHON IMPORTS
import itertools
import os
import shutil
import posixpath

# DJANGO IMPORTS
from django.core.files.move import file_move_safe
from django.core.files.base import ContentFile


class StorageMixin(object):
    """
    Adds some useful methods to the Storage class.
    """
    type_checks_slow = False

    def isdir(self, name):
        """
        Returns true if name exists and is a directory.
        """
        raise NotImplementedError()

    def isfile(self, name):
        """
        Returns true if name exists and is a regular file.
        """
        raise NotImplementedError()

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        """
        Moves safely a file from one location to another.

        If allow_ovewrite==False and new_file_name exists, raises an exception.
        """
        raise NotImplementedError()

    def makedirs(self, name):
        """
        Creates all missing directories specified by name. Analogue to os.mkdirs().
        """
        raise NotImplementedError()

    def rmtree(self, name):
        """
        Deletes a directory and everything it contains. Analogue to shutil.rmtree().
        """
        raise NotImplementedError()


class FileSystemStorageMixin(StorageMixin):

    def isdir(self, name):
        return os.path.isdir(self.path(name))

    def isfile(self, name):
        return os.path.isfile(self.path(name))

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        file_move_safe(self.path(old_file_name), self.path(new_file_name), allow_overwrite=True)

    def makedirs(self, name):
        os.makedirs(self.path(name))

    def rmtree(self, name):
        shutil.rmtree(self.path(name))


class S3BotoStorageMixin(StorageMixin):

    def isfile(self, name):
        return self.exists(name) and self.size(name) > 0

    def isdir(self, name):
        # That's some inefficient implementation...
        # If there are some files having 'name' as their prefix, then
        # the name is considered to be a directory
        if not name:  # Empty name is a directory
            return True

        if self.isfile(name):
            return False

        name = self._normalize_name(self._clean_name(name))
        dirlist = self.listdir(self._encode_name(name))

        # Check whether the iterator is empty
        for item in dirlist:
            return True
        return False

    def move(self, old_file_name, new_file_name, allow_overwrite=False):

        if self.exists(new_file_name):
            if allow_overwrite:
                self.delete(new_file_name)
            else:
                raise "The destination file '%s' exists and allow_overwrite is False" % new_file_name

        old_key_name = self._encode_name(self._normalize_name(self._clean_name(old_file_name)))
        new_key_name = self._encode_name(self._normalize_name(self._clean_name(new_file_name)))

        k = self.bucket.copy_key(new_key_name, self.bucket.name, old_key_name, preserve_acl=True)

        if not k:
            raise "Couldn't copy '%s' to '%s'" % (old_file_name, new_file_name)

        self.delete(old_file_name)

    def makedirs(self, name):
        self.save(name + "/.folder", ContentFile(""))

    def rmtree(self, name):
        name = self._normalize_name(self._clean_name(name))
        directories, files = self.listdir(self._encode_name(name))

        for key in files:
            self.delete('/'.join([name, key]))

        for dirname in directories:
            self.rmtree('/'.join([name, dirname]))


class GoogleStorageMixin(StorageMixin):

    type_checks_slow = True  # indicate that isfile/isdir should be avoided,
                             # for performance reasons, as appropriate

    def isfile(self, name):
        # Because GCS does (semi-arbitrarily) create empty blobs for
        # "folders," it's not enough to check whether the path exists;
        # and, there's not (yet) any good way to differentiate these from
        # proper files.
        #
        # It is POSSIBLE that an actual file name endswith / ...
        # HOWEVER, it is unlikely, (and kind of evil).
        #
        # (Until then), just exclude paths out-of-hand if they're empty
        # (i.e. the bucket root) OR if they end in /:
        return bool(name) and not name.endswith('/') and self.exists(name)

    def isdir(self, name):
        # That's some inefficient implementation...
        # If there are some files having 'name' as their prefix, then
        # the name is considered to be a directory
        if not name:  # Empty name is a directory
            return True

        if self.isfile(name):
            return False

        # rather than ``listdir()``, which retrieves all results, retrieve
        # blob iterator directly, and return as soon as ANY retrieved
        name = self._normalize_name(clean_name(name))
        # For bucket.list_blobs and logic below name needs to end in /
        if not name.endswith('/'):
            name += '/'

        iterator = self.bucket.list_blobs(prefix=self._encode_name(name), delimiter='/')
        dirlist = itertools.chain(iterator, iterator.prefixes)

        # Check for contents
        try:
            next(dirlist)
        except StopIteration:
            return False
        else:
            return True

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        if self.exists(new_file_name):
            if allow_overwrite:
                self.delete(new_file_name)
            else:
                raise "The destination file '%s' exists and allow_overwrite is False" % new_file_name

        old_key_name = self._encode_name(self._normalize_name(self._clean_name(old_file_name)))
        new_key_name = self._encode_name(self._normalize_name(self._clean_name(new_file_name)))

        k = self.bucket.copy_key(new_key_name, self.bucket.name, old_key_name)

        if not k:
            raise "Couldn't copy '%s' to '%s'" % (old_file_name, new_file_name)

        self.delete(old_file_name)

    def makedirs(self, name):
        self.save(name + "/.folder", ContentFile(""))

    def rmtree(self, name):
        name = self._normalize_name(self._clean_name(name))
        dirlist = self.listdir(self._encode_name(name))
        for item in dirlist:
            item.delete()

    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        return clean_name(name)


def clean_name(name):
    """
    Cleans the name so that Windows style paths work
    """
    # Normalize Windows style paths
    clean_name = posixpath.normpath(name).replace('\\', '/')

    # os.path.normpath() can strip trailing slashes so we implement
    # a workaround here.
    if name.endswith('/') and not clean_name.endswith('/'):
        # Add a trailing slash as it was stripped.
        clean_name = clean_name + '/'

    # Given an empty string, os.path.normpath() will return ., which we don't want
    if clean_name == '.':
        clean_name = ''

    return clean_name
