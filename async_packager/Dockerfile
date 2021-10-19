# Dockerfile
# FROM ubuntu
# ^ Note: hec-dss dependencies work on ubuntu linux
# Fortunately, docker image osgeo/gdal is built on Ubuntu base image
# so everything works without us having to build gdal from source ourselves 
FROM osgeo/gdal

ENV PYTHONUNBUFFERED=1 GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

RUN apt-get update \
  && apt-get install -y gfortran python3-pip git

RUN mkdir /app /output

WORKDIR /
COPY packager/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt 
RUN rm requirements.txt

# Clone USACE forked repo for pydsstools, branch specific, and install pydsstools from a wheel file
# RUN git clone -b 2.1 --single-branch https://github.com/USACE/pydsstools.git \
#   && pip install /pydsstools/dist/pydsstools-2.1-cp38-cp38-linux_x86_64.whl \
#   && rm -fR /pydsstools
# RUN git clone https://github.com/gyanz/pydsstools.git && pip install /pydsstools/dist/pydsstools-2.1-cp38-cp38-linux_x86_64.whl

COPY packager/* /app/
WORKDIR /app

CMD python3 packager.py
