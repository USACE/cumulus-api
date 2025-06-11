# FROM flyway/flyway
FROM ghcr.io/cwbi-apps/flyway:latest

COPY . /flyway/sql/

ENTRYPOINT [ "flyway" ]

CMD [ "-connectRetries=60", "migrate" ]