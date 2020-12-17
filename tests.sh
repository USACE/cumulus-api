docker run \
    -v $(pwd)/tests:/etc/newmann --network=cumulus-api_default \
    -t postman/newman run /etc/newmann/cumulus-regression.postman_collection.json \
    --environment=/etc/newmann/postman_environment.docker-compose.json