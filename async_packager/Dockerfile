# Dockerfile
# FROM ubuntu
# ^ Note: hec-dss dependencies work on ubuntu linux
# Fortunately, docker image osgeo/gdal is built on Ubuntu base image
# so everything works without us having to build gdal from source ourselves 
FROM osgeo/gdal:ubuntu-small-3.4.3

ENV PYTHONUNBUFFERED=1 GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

RUN apt-get update \
  && apt-get install -y gfortran python3-pip git

RUN mkdir /app /output

WORKDIR /
COPY packager/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt --upgrade
RUN rm requirements.txt

COPY packager /app/packager
WORKDIR /app/packager

RUN useradd appuser
USER appuser

CMD python3 packager.py
