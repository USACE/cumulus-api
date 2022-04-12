docker run \
    -v $(pwd)/docs/db-docs/schemaspy:/output \
    -v $(pwd)/docs/db-docs/schemaspy.properties:/schemaspy.properties \
    --network=cumulus-api_default schemaspy/schemaspy:latest