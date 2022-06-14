#!/usr/bin/bash

# add this dir to the stack
cd $(dirname $0)

# clean and build tiffdss
make clean
make tiffdss libtiffdss.so

# Move objects
mv -f tiffdss ../../src/cumulus_packager/bin/
printf "\nMoved tiffdss ../../src/cumulus_packager/bin\n"

mv -f libtiffdss.so /usr/lib
printf "\nMoved libtiffdss.so to /usr/lib\n"

# mv -f libhec.so /usr/lib
# printf "\nMoved libhec.so to /usr/lib\n"
