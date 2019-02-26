#!/usr/bin/env python
from __future__ import unicode_literals

import unittest

from django.conf import settings


settings.configure(
    STATIC_URL = 'https://example.com/static',
    DEBUG=True,
)


from filebrowser_safe.test_base import FileObjectTests


if __name__ == "__main__":
    unittest.main()
