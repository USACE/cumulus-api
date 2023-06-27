FROM ghcr.io/osgeo/gdal:ubuntu-full-3.7.0

# Note: 
# 1) The apt-get upgrade below is due to the latest gdal:ubuntu-full-3.7.0
#    base image being slightly out of date with patching.
# 2) The individual lines below to install/upgrade was to get
#    the packages to properly update and the docker vulnerabilities
#    to be resolved.

RUN apt-get update -y && apt-get upgrade -y \
  && apt-get install -y python3-pip git \
  && rm -rf /var/lib/apt/lists/* \
  && python3 -m pip install --no-cache-dir --upgrade pip \
  && python3 -m pip install --no-cache-dir --upgrade setuptools \
  && python3 -m pip install --no-cache-dir --upgrade wheel \
  && python3 -m pip install --no-cache-dir --upgrade pillow \
  && python3 -m pip install --no-cache-dir --upgrade numpy

RUN useradd appuser

RUN mkdir -p /app/async_geoprocess

# Cache buster
RUN echo $(date +%s)

ARG CUMULUS_GEOPROC_PIP_URL=git+https://github.com/USACE/cumulus-geoproc@main

ENV PYTHONUNBUFFERED=1

# pip install the cumulus package
RUN python3 -m pip install $CUMULUS_GEOPROC_PIP_URL

WORKDIR /app/async_geoprocess

COPY . .

USER appuser

CMD ["python3", "worker.py"]
# local testing
# CMD [ "tail", "-f", "/dev/null" ]
