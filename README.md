## Cumulus: Meteorologic Data Repository and Processing Engine

### Local Development

#### Containers

This project includes numerous docker containers to near-exactly replicate production services (for example, S3, SQS, etc.). The docker containers are orchestrated using 3 `docker-compose` files.

- **docker-compose.yml** basic minimal functionality. Database + RESTful API, SQS Messaging (ElasticMQ), etc. Naming it docker-compose.yml allows bringing the basic services online with the expected `docker-compose up --build` from the repository root directory
- **docker-compose.minio.yml** replicates S3 environment using [minio](https://github.com/minio/minio)

##### Starting All the Things (kitchen sink approach)

```
# Database and Services
docker-compose up --build
docker-compose -f docker-compose.minio.yml up --build


# Cumulus User Interface
cd site && npm start
```

These commands launch the following services, availale in the browser

| Service               | URI/Port              |
| --------------------- | --------------------- |
| Cumulus API           | http://localhost:80   |
| Pgadmin (Running SQL) | http://localhost:7000 |
| Minio Browser (S3)    | http://localhost:9000 |

---
### Documentation
#### API - https://usace.github.io/cumulus-api/api-docs/index.html
#### Database - https://usace.github.io/cumulus-api/db-docs/schemaspy/index.html
---

#### Docker-compose Mounted Directories

### Adding New Data Products

TODO
