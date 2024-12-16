FROM ghcr.io/osgeo/gdal:ubuntu-full-3.9.1

RUN apt-get update -y && apt-get install -y \
  git \
  python3-pip \
  python3-venv \
  python3-dev \
  postgresql-server-dev-all \
  libhdf5-dev \
  zlib1g-dev \
  libnetcdf-dev \
  && rm -rf /var/lib/apt/lists/*

RUN useradd appuser

RUN mkdir -p /app/async_geoprocess

# Cache buster
RUN echo $(date +%s)

ARG CUMULUS_GEOPROC_PIP_URL=git+https://github.com/USACE/cumulus-geoproc@088bd08

ENV PYTHONUNBUFFERED=1
ENV GDAL_DATA=/usr/share/gdal

# pip install the cumulus package
RUN python3 -m pip install --break-system-packages $CUMULUS_GEOPROC_PIP_URL

WORKDIR /app/async_geoprocess

COPY . .

USER appuser

CMD ["python3", "worker.py"]
# local testing
# CMD [ "tail", "-f", "/dev/null" ]
