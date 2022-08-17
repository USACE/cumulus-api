FROM osgeo/gdal:ubuntu-small-3.5.0

ENV PYTHONUNBUFFERED=1
# TODO: Set CUMULUS_GEOPROC_VERSION in Github Actions
ENV CUMULUS_GEOPROC_VERSION=develop

RUN apt-get update -y \
  && apt-get install -y python3-pip git \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/async_geoprocess
WORKDIR /app/async_geoprocess

COPY . .

# pip install/upgrade requirements before the cumulus package
# sphinx used to generate documentation from docstrings
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install git+https://github.com/USACE/cumulus-geoproc@${CUMULUS_GEOPROC_VERSION}

RUN useradd appuser && \
    mkdir -p -m 775 docs && \
    chown appuser:appuser docs

USER appuser

CMD ["python3", "worker.py"]
# local testing
# CMD [ "tail", "-f", "/dev/null" ]
