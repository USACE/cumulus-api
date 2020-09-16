#!/bin/bash

newman run \
    -e ./postman_environment.local.json \
    ./consequences-regression.postman_collection.json