
Overview
========

filebrowser_safe is a permanent fork of
`FileBrowser asset manager <https://github.com/sehmaschine/django-filebrowser>`_
for `Django <http://www.djangoproject.com/>`_, to be referenced as a
dependency for the `Mezzanine CMS for Django <http://mezzanine.jupo.org/>`_.

At the time of filebrowser_safe's creation, FileBrowser was incorrectly
packaged on `PyPI <http://pypi.python.org/pypi>`_, and had also dropped
compatibility with Django 1.1 -- filebrowser_safe was therefore created to
address these specific issues.

For further details, see
`Why are Grappelli and Filebrowser Forked? <http://mezzanine.jupo.org/docs/frequently-asked-questions.html#grappelli-filebrowser-forks>`_.

Development
===========

After cloning the repository, install the package with the extra testing requirements and run ``tox``. This will ensure you are running the tests the same way as our CI server:

.. code-block:: bash

    pip install -e ".[testing]"
    tox # Use the --parallel option to run tests in parallel

You might get some ``InterpreterNotFound`` errors due to not having all Python versions available in your system. That's okay as long as you're able to successfully run the test suite for at least one Python version.
