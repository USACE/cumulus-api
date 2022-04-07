# Dockerfile
# FROM ubuntu
FROM osgeo/gdal:ubuntu-small-latest

ENV PYTHONUNBUFFERED=1 GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

RUN apt-get update \
  && apt-get install -y python3-pip

RUN mkdir /app /output

WORKDIR /
RUN pip3 install --no-cache-dir rasterstats boto3 psycopg2-binary

COPY stats/* /app/
WORKDIR /app

RUN useradd appuser
USER appuser

CMD python3 stats.py
