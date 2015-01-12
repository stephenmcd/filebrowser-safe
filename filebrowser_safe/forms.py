from __future__ import unicode_literals
from future.builtins import super
# coding: utf-8

# imports
import os
import re

# django imports
from django import forms
from django.utils.translation import ugettext as _

# filebrowser imports
from filebrowser_safe.settings import FOLDER_REGEX


alnum_name_re = re.compile(FOLDER_REGEX)


class MakeDirForm(forms.Form):
    """
    Form for creating Folder.
    """

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(MakeDirForm, self).__init__(*args, **kwargs)

    dir_name = forms.CharField(
        widget=forms.TextInput(attrs=dict({'class': 'vTextField'},
        max_length=50, min_length=3)),
        label=_(u'Name'),
        help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'),
        required=True)

    def clean_dir_name(self):
        if self.cleaned_data['dir_name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['dir_name']):
                raise forms.ValidationError(
                    _(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # Folder must not already exist.
            if os.path.isdir(os.path.join(self.path, self.cleaned_data['dir_name'])):
                raise forms.ValidationError(_(u'The Folder already exists.'))
        return self.cleaned_data['dir_name']


class RenameForm(forms.Form):
    """
    Form for renaming Folder/File.
    """

    def __init__(self, path, file_extension, *args, **kwargs):
        self.path = path
        self.file_extension = file_extension
        super(RenameForm, self).__init__(*args, **kwargs)

    name = forms.CharField(
        widget=forms.TextInput(attrs=dict({'class': 'vTextField'},
        max_length=50, min_length=3)),
        label=_(u'New Name'),
        help_text=_('Only letters, numbers, underscores, spaces and hyphens are allowed.'),
        required=True)

    def clean_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if (not alnum_name_re.search(self.cleaned_data['name']) or
                not alnum_name_re.search(self.path)):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            #  folder/file must not already exist.
            if os.path.isdir(os.path.join(self.path, self.cleaned_data['name'])):
                raise forms.ValidationError(_(u'The Folder already exists.'))
            elif os.path.isfile(os.path.join(self.path, self.cleaned_data['name'] + self.file_extension)):
                raise forms.ValidationError(_(u'The File already exists.'))
        return self.cleaned_data['name']
