# Dockerfile
# FROM ubuntu
# ^ Note: hec-dss dependencies work on ubuntu linux
# Fortunately, docker image osgeo/gdal is built on Ubuntu base image
# so everything works without us having to build gdal from source ourselves 
FROM osgeo/gdal:ubuntu-small-3.4.3

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV PACKAGE=async_packager

# update, install and clean up
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y gcc-10 gfortran zlib1g-dev make python-pip3 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install /app/${PACKAGE}/


# RUN mkdir /app /output

# WORKDIR /
# COPY packager/requirements.txt ./
# RUN pip3 install --no-cache-dir -r requirements.txt --upgrade
# RUN rm requirements.txt

# COPY packager /app/packager
# WORKDIR /app/packager

RUN useradd appuser
USER appuser

# CMD python3 packager.py
CMD [ "tail", "-f" , "/dev/null" ]
