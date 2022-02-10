FROM flyway/flyway

COPY . /flyway/sql/

RUN ls /flyway/sql

ENTRYPOINT [ "flyway" ]

CMD [ "-connectRetries=60", "migrate" ]