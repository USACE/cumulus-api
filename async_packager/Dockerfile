# Packager
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.7.0 AS base

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV GDAL_DATA=/usr/share/gdal
ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

ENV PACKAGE=async_packager

# solving possible issue of ATP behind a proxy
RUN cat <<EOF > /etc/apt/apt.conf.d/99proxy
Acquire::http::Pipeline-Depth 0;
Acquire::http::No-Cache true;
Acquire::BrokenProxy true;
EOF

# update and install other dependencies
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y python3-pip curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir --upgrade wheel && \
    pip install --no-cache-dir --upgrade pillow && \
    pip install --no-cache-dir --upgrade hecdss
    # pip install --no-cache-dir --upgrade numpy


RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# pip install the package and upgrade outdated packages
RUN pip3 install /app/${PACKAGE}/

RUN useradd appuser && \
    mkdir -p -m 775 docs && \
    chown appuser:appuser docs

USER appuser

CMD ["./packager.py"]
