from __future__ import unicode_literals
from future.builtins import str, super

import os
import datetime

from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models.fields import Field
from django.db.models.fields.files import FileDescriptor
from django.forms.widgets import Input
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from filebrowser_safe.settings import *
from filebrowser_safe.base import FieldFileObject
from filebrowser_safe.functions import get_directory


class FileBrowseWidget(Input):
    input_type = 'text'

    class Media:
        js = (os.path.join(URL_FILEBROWSER_MEDIA, 'js/AddFileBrowser.js'), )

    def __init__(self, attrs=None):
        self.directory = attrs.get('directory', '')
        self.extensions = attrs.get('extensions', '')
        self.format = attrs.get('format', '')
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        directory = self.directory
        if self.directory:
            if callable(self.directory):
                directory = self.directory()
            directory = os.path.normpath(datetime.datetime.now().strftime(directory))
            fullpath = os.path.join(get_directory(), directory)
            if not default_storage.isdir(fullpath):
                default_storage.makedirs(fullpath)
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        final_attrs['search_icon'] = URL_FILEBROWSER_MEDIA + 'img/filebrowser_icon_show.gif'
        final_attrs['directory'] = directory
        final_attrs['extensions'] = self.extensions
        final_attrs['format'] = self.format
        final_attrs['DEBUG'] = DEBUG
        return render_to_string("filebrowser/custom_field.html", dict(locals(), MEDIA_URL=MEDIA_URL))


class FileBrowseFormField(forms.CharField):
    widget = FileBrowseWidget

    default_error_messages = {
        'extension': _(u'Extension %(ext)s is not allowed. Only %(allowed)s is allowed.'),
    }

    def __init__(self, max_length=None, min_length=None,
                 directory=None, extensions=None, format=None,
                 *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        self.directory = directory
        self.extensions = extensions
        if format:
            self.format = format or ''
            self.extensions = extensions or EXTENSIONS.get(format)
        super(FileBrowseFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(FileBrowseFormField, self).clean(value)
        if value == '':
            return value
        file_extension = os.path.splitext(value)[1].lower().split("?")[0]
        if self.extensions and not file_extension in self.extensions:
            raise forms.ValidationError(self.error_messages['extension'] % {'ext': file_extension, 'allowed': ", ".join(self.extensions)})
        return value


class FileBrowseField(Field):
    # These attributes control how the field is accessed on a model instance.
    # Due to contribute_to_class, FileDescriptor will cause this field to be
    # represented by a FileFieldObject on model instances.
    # Adapted from django.db.models.fields.files.FileField.
    attr_class = FieldFileObject
    descriptor_class = FileDescriptor

    def __init__(self, *args, **kwargs):
        self.directory = kwargs.pop('directory', '')
        self.extensions = kwargs.pop('extensions', '')
        self.format = kwargs.pop('format', '')
        self.storage = kwargs.pop('storage', default_storage)
        super(FileBrowseField, self).__init__(*args, **kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        return smart_str(value)

    def get_manipulator_field_objs(self):
        return [oldforms.TextField]

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        attrs = {
            'directory': self.directory,
            'extensions': self.extensions,
            'format': self.format,
            'storage': self.storage,
        }
        defaults = {
            'form_class': FileBrowseFormField,
            'widget': FileBrowseWidget(attrs=attrs),
            'directory': self.directory,
            'extensions': self.extensions,
            'format': self.format
        }
        defaults.update(kwargs)
        return super(FileBrowseField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name, **kwargs):
        """
        From django.db.models.fields.files.FileField.contribute_to_class
        """
        super(FileBrowseField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))
