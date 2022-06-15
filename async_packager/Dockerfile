# Compile DSS
FROM ubuntu:18.04 AS cbuilder

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y gcc gfortran zlib1g-dev make git && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --branch 7-IJ --single-branch https://github.com/HydrologicEngineeringCenter/hec-dss.git
# run only for local testing
RUN git clone --branch master --single-branch https://github.com/HydrologicEngineeringCenter/dss-test-data.git

COPY Makefile /

RUN make

# Packager
FROM osgeo/gdal:ubuntu-small-3.4.3 as packager

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV PACKAGE=async_packager

# update, install and clean up
    # apt-get -y upgrade && \
RUN apt-get -y update && \
    apt-get install -y gcc gfortran python3-pip libffi-dev gdb && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# Copy archives and headers from cbuilder
COPY --from=cbuilder --chown=root:root /hec-dss/heclib/heclib_c/Output/libhec_c.a /usr/lib
COPY --from=cbuilder --chown=root:root /hec-dss/heclib/heclib_f/Output/libhec_f.a /usr/lib
COPY --from=cbuilder --chown=root:root /hec-dss/heclib/heclib_c/src/headers /hec-dss/heclib/heclib_c/src/headers
# copy only for local testing
COPY --from=cbuilder --chown=root:root /dss-test-data/tiff/*.tif /dss-test-data/tiff/

RUN bash ./tiffdss/src/make.sh

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install /app/${PACKAGE}/

# RUN useradd appuser
# USER appuser

# CMD python3 packager.py
# local testing only
CMD [ "tail", "-f" , "/dev/null" ]
