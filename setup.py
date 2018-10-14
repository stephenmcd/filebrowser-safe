import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test


class TestCommand(test):

    def run_tests(self):
        import django
        from django.conf import settings
        from django.test.utils import get_runner

        os.environ['DJANGO_SETTINGS_MODULE'] = 'filebrowser_safe.tests.settings'
        django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        failures = test_runner.run_tests(["filebrowser_safe.tests"])
        sys.exit(bool(failures))


setup(
    name="filebrowser_safe",
    version="0.5.0",
    description="A snapshot of the filebrowser_3 branch of django-filebrowser, "
                "packaged as a dependency for the Mezzanine CMS for Django.",
    long_description=open("README.rst").read(),
    author="Patrick Kranzlmueller, Axel Swoboda (vonautomatisch)",
    author_email="werkstaetten@vonautomatisch.at",
    maintainer="Stephen McDonald",
    maintainer_email="stephen.mc@gmail.com",
    url="http://github.com/stephenmcd/filebrowser-safe",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'django >= 1.11',
        'grappelli_safe >= 0.5.0',
        'mezzanine',
    ],
    cmdclass={"test": TestCommand},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
