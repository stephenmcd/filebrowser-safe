#!/usr/bin/env python
from __future__ import unicode_literals

import unittest


class FileObjectTests(unittest.TestCase):
    """Verify `FileObject` features."""

    def test_size_is_filesize(self):
        from filebrowser_safe.base import FileObject
        fileobj = FileObject('foo/bar.jpg', size=17834)
        self.assertEqual(fileobj.size, 17834)
        self.assertEqual(fileobj.filesize, 17834)
