#!/usr/bin/env bash

# Construct the DATABASE_URL using environment variables
export DATABASE_URL="postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}/${PGDATABASE}?application_name=pg_featureserv&options=-c+role%3D${PGTARGETROLE}"

# Debug - DO NOT enable this and commit, we don't want it in the AWS logs)
# echo "DATABASE_URL is: $DATABASE_URL"

# Now, execute the default command (pg_featureserv or any other service)
exec "$@"