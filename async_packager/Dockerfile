# Packager
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.7.0 as base

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

ENV PACKAGE=async_packager

ENV TIFFDSS_VERSION=v0.2.0
ENV TIFFDSS=tiffdss_ubuntu-latest

# update and install other dependencies
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y python3-pip curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir --upgrade wheel && \
    pip install --no-cache-dir --upgrade pillow && \
    pip install --no-cache-dir --upgrade numpy


RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# pip install the package and upgrade outdated packages
RUN pip3 install /app/${PACKAGE}/

# get libtiffdss.so
RUN curl -L https://github.com/HydrologicEngineeringCenter/tiffdss/releases/download/${TIFFDSS_VERSION}/${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz \
    --output ${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz && \
    tar -zxvf ${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz && \
    mv libtiffdss.so /usr/lib/ && \
    rm -f ${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz tiffdss *.o

RUN useradd appuser && \
    mkdir -p -m 775 docs && \
    chown appuser:appuser docs

USER appuser

CMD ["./packager.py"]
