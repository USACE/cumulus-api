# Packager
ARG GDAL_TAG=ubuntu-full-3.13.1


FROM ghcr.io/osgeo/gdal:${GDAL_TAG} AS builder

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

#GDAL
ENV GDAL_DATA=/usr/share/gdal
ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

# packager
ENV USERNAME=packager
ENV PACKAGER=/opt/packager
ENV PACKAGER_VENV=${PACKAGER}/venv

ENV PATH=${PACKAGER_VENV}/bin:$PATH

#ENV PACKAGE=async_packager

# solving possible issue of ATP behind a proxy
RUN cat <<EOF > /etc/apt/apt.conf.d/99proxy
Acquire::http::Pipeline-Depth 0;
Acquire::http::No-Cache true;
Acquire::BrokenProxy true;
EOF


# update and install other dependencies
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y python3-venv \
    && apt-get remove python3-pil -y \
    && apt clean

# Remove unused Arrow ADBC drivers and the stray pebble binary shipped by the GDAL
# ubuntu-full image. GDAL builds the ADBC drivers as an optional component; nothing in
# cumulus-api or cumulus-geoproc opens an ADBC connection, and pebble is not part of GDAL's
# published Dockerfile at all. They are Go binaries and account for the large majority of
# this image's CVE findings.
RUN rm -f /usr/bin/pebble /usr/lib/x86_64-linux-gnu/libadbc_driver_*.so*

# install package in venv
COPY . ${PACKAGER}/pkg

RUN python3 -m venv --system-site-packages ${PACKAGER_VENV} \
    && . activate \
    && pip install --upgrade pip \
    && pip install ${PACKAGER}/pkg/ \
    && pip install hecdss

RUN groupadd -r ${USERNAME} && \
    useradd -g ${USERNAME} -ms /bin/bash ${USERNAME}

WORKDIR ${PACKAGER}

# packager and run it
COPY ./packager.py ./

USER ${USERNAME}:${USERNAME}

ENTRYPOINT ["python3", "packager.py"]
