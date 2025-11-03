# Packager
ARG GDAL_TAG=ubuntu-full-3.9.1


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
    && apt-get install -y python3.12-venv \
    && apt-get remove python3-pil -y \
    && apt clean

# install package in venv
COPY . ${PACKAGER}/pkg

# Copy and install custom hecdss wheel
COPY hecdss-0.1.28-py3-none-any.whl ${PACKAGER}/

RUN python3 -m venv --system-site-packages ${PACKAGER_VENV} \
    && . activate \
    && pip install ${PACKAGER}/hecdss-0.1.28-py3-none-any.whl \
    && pip install ${PACKAGER}/pkg/

RUN groupadd -r ${USERNAME} && \
    useradd -g ${USERNAME} -ms /bin/bash ${USERNAME}

WORKDIR ${PACKAGER}

# packager and run it
COPY ./packager.py ./

USER ${USERNAME}:${USERNAME}

ENTRYPOINT ["python3", "packager.py"]
