# Run Tests For Admin User
docker run \
    -v $(pwd)/tests:/etc/newman --network=cumulus-api_default \
    --entrypoint /bin/bash -t postman/newman:ubuntu \
    -c "npm i -g newman-reporter-htmlextra;
        newman run /etc/newman/cumulus-regression-admin.postman_collection.json \
        --environment=/etc/newman/postman_environment.docker-compose.json \
        --reporter-htmlextra-browserTitle 'Cumulus' \
        --reporter-htmlextra-title 'Cumulus Regression Tests; Admin Account' \
        --reporter-htmlextra-titleSize 4 \
        -r htmlextra --reporter-htmlextra-export /etc/newman/cumulus-admin.html"

# Run Tests For Non-Admin User
docker run \
    -v $(pwd)/tests:/etc/newman --network=cumulus-api_default \
    --entrypoint /bin/bash -t postman/newman:ubuntu \
    -c "npm i -g newman-reporter-htmlextra;
        newman run /etc/newman/cumulus-regression-user.postman_collection.json \
        --environment=/etc/newman/postman_environment.docker-compose.json \
        --reporter-htmlextra-browserTitle 'Cumulus' \
        --reporter-htmlextra-title 'Cumulus Regression Tests; User Account' \
        --reporter-htmlextra-titleSize 4 \
        -r htmlextra --reporter-htmlextra-export /etc/newman/cumulus-user.html"