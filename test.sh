#!/bin/sh

# Install latest mezzanine master branch.
mezzanine="./mezzanine-git"
if [ -d $mezzanine ]; then
        git -C $mezzanine pull
else
        git clone --branch master --depth 1 https://github.com/stephenmcd/mezzanine.git $mezzanine
fi
pip install -U $mezzanine

# Install filebrowser-safe.
pip install -U -e .

# Run mezzanine tests.
(cd $mezzanine && python setup.py test)
