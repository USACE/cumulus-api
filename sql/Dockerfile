# FROM flyway/flyway
FROM redgate/flyway:latest-alpine

COPY . /flyway/sql/

ENTRYPOINT [ "flyway" ]

CMD [ "-connectRetries=60", "migrate" ]