## Cumulus: Meteorologic Data Repository and Processing Engine

### Local Development

#### Containers

This project includes numerous docker containers to near-exactly replicate production services (for example, S3, SQS, etc.). The docker containers are orchestrated using 3 `docker-compose` files.

- **docker-compose.yml** basic minimal functionality. Database + RESTful API, SQS Messaging (ElasticMQ), etc. Naming it docker-compose.yml allows bringing the basic services online with the expected `docker-compose up --build` from the repository root directory
- **docker-compose.minio.yml** replicates S3 environment using [minio](https://github.com/minio/minio)
- **docker-compose.airflow.yml** launches apache airflow containers. Apache airflow is used for workflows/pipelines

##### Starting All the Things (kitchen sink approach)

```
# Database and Services
docker-compose up --build
docker-compose -f docker-compose.minio.yml up --build
docker-compose -f docker-compose.airflow.yml up --build

# Cumulus User Interface
cd site && npm start
```

These commands launch the following services, availale in the browser

| Service               | URI/Port              |
| --------------------- | --------------------- |
| Cumulus API           | http://localhost:80   |
| Cumulus UI            | http://localhost:3000 |
| Pgadmin (Running SQL) | http://localhost:7000 |
| Airflow Admin         | http://localhost:8000 |
| Minio Browser (S3)    | http://localhost:9000 |
| Nginx                 | http://localhost:8080 |

#### Docker-compose Mounted Directories

##### Airflow Scheduler

- ./airflow/logs:/opt/airflow/logs : Mounts logs in container to local file system for easy review when troubleshooting

### Adding New Data Products

TODO
