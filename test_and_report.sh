# Run Tests For Admin User
docker run \
    -v $(pwd)/tests:/etc/newman --network=cumulus-api_default \
    --entrypoint /bin/bash -t postman/newman:ubuntu \
    -c "newman run /etc/newman/cumulus-regression-admin.postman_collection.json \
        --environment=/etc/newman/postman_environment.docker-compose.json"

# Run Tests For Non-Admin User
docker run \
    -v $(pwd)/tests:/etc/newman --network=cumulus-api_default \
    --entrypoint /bin/bash -t postman/newman:ubuntu \
    -c "newman run /etc/newman/cumulus-regression-user.postman_collection.json \
        --environment=/etc/newman/postman_environment.docker-compose.json"
