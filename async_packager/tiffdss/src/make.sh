#!/usr/bin/bash

# add this dir to the stack
cd $(dirname $0)

# clean and build tiffdss
make clean
make tiffdss
make libtiffdss.so

# copy the binary over to the cumulus packager package
if [ -x tiffdss ]
then
    mv -f tiffdss ../../src/cumulus_packager/bin/
    mv -f libtiffdss.so ../../src/cumulus_packager/bin/
    printf "\nMoved tiffdss and libtiffdss.so to ../../src/cumulus_packager/bin\n"
fi
