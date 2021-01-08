#!/bin/bash

# Initialize Airflow Schema
airflow db reset -y
airflow db init

# Create Airflow User
airflow users create \
    --role Admin \
    --username airflow \
    --email airflow@airflow.com \
    --firstname airflow \
    --lastname airflow \
    --password airflow

# Create Connection for local_minio
# S3 Standin When Developing
airflow connections add 'local_minio' \
    --conn-type 'aws' \
    --conn-extra '{"host": "http://minio:9000", "region": "us-east-1"}' \
    --conn-login 'AKIAIOSFODNN7EXAMPLE' \
    --conn-password 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'