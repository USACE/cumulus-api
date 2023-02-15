# Packager
FROM osgeo/gdal:ubuntu-small-3.6.1

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

ENV PACKAGE=async_packager

ENV TIFFDSS_VERSION=v0.1.1
ENV TIFFDSS=tiffdss_ubuntu-latest

# update and install other dependencies
RUN apt-get -y update && \
    apt-get install -y python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# pip install/upgrade
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install /app/${PACKAGE}/

# get libtiffdss.so
RUN curl -L https://github.com/HydrologicEngineeringCenter/tiffdss/releases/download/${TIFFDSS_VERSION}/${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz \
    --output ${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz && \
    tar -zxvf ${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz && \
    mv libtiffdss.so /usr/lib/ &&\
    rm -f ${TIFFDSS}_${TIFFDSS_VERSION}.tar.gz tiffdss *.o

RUN useradd appuser && \
    mkdir -p -m 775 docs && \
    chown appuser:appuser docs

USER appuser

CMD python3 packager.py
# local testing only
# CMD [ "tail", "-f" , "/dev/null" ]
