ARG GDAL_TAG=ubuntu-full-3.13.1
ARG GEOPROC_PACKAGE=main:geoproc

# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# builder
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
FROM ghcr.io/osgeo/gdal:${GDAL_TAG} AS builder
ARG GEOPROC_PACKAGE

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

# GDAL
ENV GDAL_DATA=/usr/share/gdal

# geoproc
ENV USERNAME=geoproc
ENV GEOPROC=/opt/geoproc
ENV GEOPROC_VENV=${GEOPROC}/venv

ENV PATH=${GEOPROC_VENV}/bin:$PATH

# solving possible issue of ATP behind a proxy
RUN cat <<EOF > /etc/apt/apt.conf.d/99proxy
Acquire::http::Pipeline-Depth 0;
Acquire::http::No-Cache true;
Acquire::BrokenProxy true;
EOF

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install python3-venv -y \
    && apt-get remove python3-pil -y \
    && apt clean

# Remove unused Arrow ADBC drivers and the stray pebble binary shipped by the GDAL
# ubuntu-full image. GDAL builds the ADBC drivers as an optional component; nothing in
# cumulus-api or cumulus-geoproc opens an ADBC connection, and pebble is not part of GDAL's
# published Dockerfile at all. They are Go binaries and account for the large majority of
# this image's CVE findings.
RUN rm -f /usr/bin/pebble /usr/lib/x86_64-linux-gnu/libadbc_driver_*.so*

# create the user account
RUN groupadd -r ${USERNAME} && \
    useradd -g ${USERNAME} -ms /bin/bash ${USERNAME}

WORKDIR ${GEOPROC}

# get the cumulus-geoproc package
ADD --keep-git-dir=false --chown=${USERNAME}:${USERNAME} https://github.com/USACE/cumulus-geoproc.git#${GEOPROC_PACKAGE} ${GEOPROC}/pkg

# install package in venv
RUN python3 -m venv --system-site-packages ${GEOPROC_VENV} \
    && . activate \
    && pip install --upgrade pip \
    && pip install ${GEOPROC}/pkg/

# Cache buster
# RUN echo $(date +%s)

COPY ./worker.py ./

USER ${USERNAME}:${USERNAME}

ENTRYPOINT ["python3", "worker.py"]
