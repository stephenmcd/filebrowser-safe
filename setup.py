
from setuptools import setup, find_packages

setup(
    name="filebrowser_safe",
    version="0.4.4",
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
)
