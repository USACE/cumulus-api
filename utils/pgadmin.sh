#!/bin/bash
# Convenience script to start pgadmin4 container on localhost:8080
docker run -d -p "1337:80" \
    -e PGADMIN_DEFAULT_EMAIL=postgres@postgres.com \
    -e PGADMIN_DEFAULT_PASSWORD=postgres \
    dpage/pgadmin4:4.27