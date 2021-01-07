docker run \
    -v $(pwd)/tests:/etc/newman --network=cumulus-api_default \
    --entrypoint /bin/bash -t postman/newman:ubuntu \
    -c "npm i -g newman-reporter-htmlextra;
        newman run /etc/newman/cumulus-regression.postman_collection.json \
        --environment=/etc/newman/postman_environment.docker-compose.json \
        --reporter-htmlextra-browserTitle 'Cumulus' \
        --reporter-htmlextra-title 'Cumulus Regression Tests' \
        --reporter-htmlextra-titleSize 4 \
        -r htmlextra --reporter-htmlextra-export /etc/newman/cumulus"