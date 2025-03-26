ARG GDAL_TAG=ubuntu-full-3.9.1
ARG GEOPROC_PACKAGE=develop:geoproc

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

RUN apt-get -y update \
  && apt-get install python3.12-venv -y \
  && apt-get remove python3-pil -y \
  && apt clean

# create the user account
RUN groupadd -r ${USERNAME} && \
  useradd -g ${USERNAME} -ms /bin/bash ${USERNAME}

WORKDIR ${GEOPROC}

# get the cumulus-geoproc package
ADD --keep-git-dir=false --chown=${USERNAME}:${USERNAME} https://github.com/USACE/cumulus-geoproc.git#${GEOPROC_PACKAGE} ${GEOPROC}/pkg

# install package in venv
RUN python3 -m venv --system-site-packages ${GEOPROC_VENV} \
  && . activate \
  && pip install ${GEOPROC}/pkg/

# Cache buster
# RUN echo $(date +%s)

COPY ./worker.py ./

USER ${USERNAME}:${USERNAME}

ENTRYPOINT ["python3", "worker.py"]
