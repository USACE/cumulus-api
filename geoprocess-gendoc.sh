#!/bin/bash

# build the geoprocess image
docker-compose build geoprocess

# run the gen doc image
docker run -d --rm \
    -v ${PWD}/docs/async_geoprocess/cumulus_geoproc:/app/async_geoprocess/docs/cumulus_geoproc \
    --name cumulus-api_geoproc_docs cumulus-api_geoprocess /bin/bash -c "./gendoc.sh"
