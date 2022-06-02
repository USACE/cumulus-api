#!/usr/bin/bash

# add this dir to the stack
pushd $(dirname $0)

# clean and build tiffdss
make clean
make

# remove this dir from the stack
popd
