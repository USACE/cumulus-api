#!/bin/bash

# build the packager image
docker-compose build packager

# run the gen doc image
docker run -d --rm \
    -v ${PWD}/docs/async_packager/cumulus_packager:/app/async_packager/docs/cumulus_packager \
    --name cumulus-api_packager_docs cumulus-api_packager /bin/bash -c "./gendoc.sh"
