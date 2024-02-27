#!/bin/bash

if [ -z "$S3_ENDPOINT_URL" ]
then
    CMD="aws s3 sync s3://${S3_BUCKET}/${S3_PREFIX} /data/ --exact-timestamps --delete"
else
    CMD="aws s3 --endpoint-url ${S3_ENDPOINT_URL} sync s3://${S3_BUCKET}/${S3_PREFIX} /data/ --exact-timestamps --delete"
fi

# Sleep for 20 seconds; Used in local development to wait for Minio to initialize
echo "Sleeping for 20 Seconds ..."
sleep 20

while true
do
    echo "Sync With Bucket ${LDM_AWS_S3_BUCKET}; $(date)"
    $CMD
    
    if [[ $SYNC_SECONDS -eq 0 ]]
    then
        echo "Sync Complete; $(date)"
        exit 0
    else
        echo "Waiting ${SYNC_SECONDS} seconds until next sync."
        sleep $SYNC_SECONDS
    fi
    
done