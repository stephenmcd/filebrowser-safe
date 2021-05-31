import os
import posixpath
import shutil

from django.core.files.base import ContentFile
from django.core.files.move import file_move_safe

FILE_EXISTS_MSG = "The destination file '{}' exists and allow_overwrite is False"


class StorageMixin:
    """
    Adds some useful methods to the Storage class.
    """

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

        If allow_overwrite==False and new_file_name exists, raises an exception.
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
        file_move_safe(
            self.path(old_file_name), self.path(new_file_name), allow_overwrite=True
        )

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
                raise FILE_EXISTS_MSG.format(new_file_name)

        old_key_name = self._encode_name(
            self._normalize_name(self._clean_name(old_file_name))
        )
        new_key_name = self._encode_name(
            self._normalize_name(self._clean_name(new_file_name))
        )

        k = self.bucket.copy_key(
            new_key_name, self.bucket.name, old_key_name, preserve_acl=True
        )

        if not k:
            raise f"Couldn't copy '{old_file_name}' to '{new_file_name}'"

        self.delete(old_file_name)

    def makedirs(self, name):
        self.save(name + "/.folder", ContentFile(""))

    def rmtree(self, name):
        name = self._normalize_name(self._clean_name(name))
        directories, files = self.listdir(self._encode_name(name))

        for key in files:
            self.delete("/".join([name, key]))

        for dirname in directories:
            self.rmtree("/".join([name, dirname]))


class GoogleStorageMixin(StorageMixin):
    def isfile(self, name):
        return self.exists(name)

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
                raise FILE_EXISTS_MSG.format(new_file_name)

        old_key_name = self._encode_name(
            self._normalize_name(self._clean_name(old_file_name))
        )
        new_key_name = self._encode_name(
            self._normalize_name(self._clean_name(new_file_name))
        )

        k = self.bucket.copy_key(new_key_name, self.bucket.name, old_key_name)

        if not k:
            raise f"Couldn't copy '{old_file_name}' to '{new_file_name}'"

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
    clean_name = posixpath.normpath(name).replace("\\", "/")

    # os.path.normpath() can strip trailing slashes so we implement
    # a workaround here.
    if name.endswith("/") and not clean_name.endswith("/"):
        # Add a trailing slash as it was stripped.
        clean_name = clean_name + "/"

    # Given an empty string, os.path.normpath() will return ., which we don't want
    if clean_name == ".":
        clean_name = ""

    return clean_name
