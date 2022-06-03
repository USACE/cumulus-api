#!/usr/bin/bash

# add this dir to the stack
cd $(dirname $0)

# clean and build tiffdss
make clean
make

# copy the binary over to the cumulus packager package
if [ -x tiffdss ]
then
    mv -f tiffdss ../../src/cumulus_packager/bin/tiffdss
    printf "\nMoved tiffdss to ../../src/cumulus_packager/bin/tiffdss\n"
fi
