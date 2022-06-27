#!/bin/bash

HEADER="Cumulus Geoprocess"
AUTHOR="CRREL"
VERSION=0.1.0

printf "***** sphinx-apidoc *****\n"
sphinx-apidoc -a -f -e -M -F -d 6 -H"$HEADER" -A"$AUTHOR" -V"$VERSION" \
    --extensions "sphinx.ext.napoleon" \
    -o ./docs/cumulus_geoproc \
    ./src/cumulus_geoproc

printf "***** sphinx-build *****\n"
sphinx-build -a -E -D html_theme=sphinx_rtd_theme -b html \
    ./docs/cumulus_geoproc \
    ./docs/cumulus_geoproc/_build/html
