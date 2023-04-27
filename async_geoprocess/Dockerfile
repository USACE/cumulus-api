FROM osgeo/gdal:ubuntu-full-3.5.3

RUN apt-get update -y \
  && apt-get install -y python3-pip git \
  && rm -rf /var/lib/apt/lists/*

RUN useradd appuser

RUN mkdir -p /app/async_geoprocess

# Cache buster
RUN echo $(date +%s)

ARG CUMULUS_GEOPROC_PIP_URL=git+https://github.com/USACE/cumulus-geoproc@03137e8
ENV PYTHONUNBUFFERED=1

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools \
  && python3 -m pip install $CUMULUS_GEOPROC_PIP_URL

WORKDIR /app/async_geoprocess

COPY . .

USER appuser

CMD ["python3", "worker.py"]
# local testing
# CMD [ "tail", "-f", "/dev/null" ]
