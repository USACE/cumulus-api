#!/usr/bin/env bash

today=`date +"%Y-%m-%d"`
S3_PATH=${AWS_S3_BUCKET}/${CUMULUS_S3_DB_EXPORT_DIR}/${today}

printf "\n1) Copying export from $S3_PATH/export.dump to local storage (import.dump).\n\n"
# Copy the dump/export file to local storage before starting the restore/import
aws --endpoint-url $AWS_S3_ENDPOINT s3 cp s3://$S3_PATH/export.dump /app/data/import.dump

printf "\n2) Running pg_restore on import.dump.\n\n"
pg_restore --clean --dbname=$PGDATABASE -h $PGHOST --verbose --format=c --jobs=1 --username $PGUSER --schema $SCHEMA  < /app/data/import.dump > /app/data/import.log 2>&1

aws --endpoint-url $AWS_S3_ENDPOINT s3 cp /app/data/import.log s3://$S3_PATH/import.log

printf "\nDONE.  Any errors can be found in ${S3_PATH}/import.log\n\n"