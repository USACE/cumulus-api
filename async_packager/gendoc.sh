#!/bin/bash

HEADER="Cumulus Packager"
AUTHOR="CRREL"
VERSION=0.1.0

printf "***** sphinx-apidoc *****\n"
sphinx-apidoc -a -f -e -M -F -d 6 -H"$HEADER" -A"$AUTHOR" -V"$VERSION" \
    --extensions "sphinx.ext.napoleon" \
    -o ./docs/cumulus_packager \
    ./src/cumulus_packager

printf "***** sphinx-build *****\n"
sphinx-build -a -E -D html_theme=sphinx_rtd_theme -b html \
    ./docs/cumulus_packager \
    ./docs/cumulus_packager/_build/html
