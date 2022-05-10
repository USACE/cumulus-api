#!/usr/bin/env bash

mkdir -p /app/async_geoprocess

git clone --branch ${GIT_BRANCH} --single-branch ${GIT_REPO_URL} /cumulus-api

cp -r /cumulus-api/async_geoprocess/* /app/async_geoprocess

rm -r /cumulus-api

python3 -m pip install --upgrade pip wheel setuptools --user && python3 -m pip install /app/async_geoprocess/ --user