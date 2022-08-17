FROM osgeo/gdal:ubuntu-small-3.5.0

ARG CUMULUS_GEOPROC_PIP_URL
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
  && apt-get install -y python3-pip git \
  && rm -rf /var/lib/apt/lists/*

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools \
  && python3 -m pip install $CUMULUS_GEOPROC_PIP_URL

RUN useradd appuser

RUN mkdir -p /app/async_geoprocess

WORKDIR /app/async_geoprocess

COPY . .

USER appuser

CMD ["python3", "worker.py"]
# local testing
# CMD [ "tail", "-f", "/dev/null" ]
