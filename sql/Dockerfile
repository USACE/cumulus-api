# FROM flyway/flyway
FROM flyway/flyway:latest-alpine

COPY . /flyway/sql/

ENTRYPOINT [ "flyway" ]

CMD [ "-connectRetries=60", "migrate" ]