FROM osgeo/gdal:ubuntu-small-3.5.0

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/async_geoprocess

WORKDIR /app/async_geoprocess

COPY . .

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools \
  && python3 -m pip install /app/async_geoprocess/

RUN useradd appuser
USER appuser

CMD ["python3", "worker.py"]
