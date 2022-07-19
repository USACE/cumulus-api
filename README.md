# Statistics Minimum Viable Product

Type docker compose up --build. This will bring up Minio (S3), ElasticMQ (SQS), and statistics containers.

Once services are online, run `python3 ./send_message.py` from this directory to simulate an SQS message. This message represents running of basic geospatial statistics (min,max,mean) for the guyandotte river watershed for July 18th, 2022 17hours UTC

There is scaffold in the code for writing output to a target (e.g. API, Grafana Mimir, or Otherwise), but implementation details for this have not been determined yet.

