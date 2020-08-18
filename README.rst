
Overview
========

filebrowser_safe is a permanent fork of
`FileBrowser asset manager <https://github.com/sehmaschine/django-filebrowser>`_
for `Django <https://www.djangoproject.com/>`_, to be referenced as a
dependency for the `Mezzanine CMS for Django <https://mezzanine.jupo.org/>`_.

At the time of filebrowser_safe's creation, FileBrowser was incorrectly
packaged on `PyPI <https://pypi.python.org/pypi>`_, and had also dropped
compatibility with Django 1.1 -- filebrowser_safe was therefore created to
address these specific issues.

For further details, see
`Why are Grappelli and Filebrowser Forked? <https://mezzanine.jupo.org/docs/frequently-asked-questions.html#grappelli-filebrowser-forks>`_.

Development
===========

After cloning the repository, install the package with the extra testing requirements and run ``tox``. This will ensure you are running the tests the same way as our CI server:

.. code-block:: bash

    pip install -e ".[testing]"
    tox # Use the --parallel option to run tests in parallel (faster)

You might get some ``InterpreterNotFound`` errors due to not having all Python versions available in your system. That's okay as long as you're able to successfully run the test suite for at least one Python version.

Python code is enforced with ``flake8`` and  ``black``. ``tox`` will verify both for you. For your convenience you can run the command ``tox -e format`` to fix most (but not all) linter errors. Alternatively you can configure your code editor to lint and format according to the rules defined in ``setup.cfg`` to catch code style errors as you develop.

When you are ready to contribute your changes create and submit a pull request for review. This will run all tests in all supported Python versions and alert if any of them fail.
