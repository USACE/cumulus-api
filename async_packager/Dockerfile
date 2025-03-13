ARG GDAL_TAG=ubuntu-full-3.9.1
ARG TIFFDSS_VERSION=v0.2.2

# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# builder
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
FROM ghcr.io/osgeo/gdal:${GDAL_TAG} AS builder
ARG TIFFDSS_VERSION

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

# GDAL
ENV GDAL_DATA=/usr/share/gdal
ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

# packager
ENV USERNAME=packager
ENV PACKAGER=/opt/packager
ENV PACKAGER_VENV=${PACKAGER}/venv

ENV PATH=${PACKAGER_VENV}/bin:$PATH

# update and install other dependencies
RUN apt-get -y update \
    # && apt-get -y upgrade \
    && apt-get install -y python3.12-venv \
    && apt-get remove python3-pil -y \
    && apt clean

RUN groupadd -r ${USERNAME} && \
    useradd -g ${USERNAME} -ms /bin/bash ${USERNAME}

WORKDIR ${PACKAGER}

# install package in venv
COPY ./packager ${PACKAGER}/pkg
RUN python3 -m venv --system-site-packages ${PACKAGER_VENV} \
    && . activate \
    && pip install ${PACKAGER}/pkg/

# get libtiffdss.so
ADD https://github.com/HydrologicEngineeringCenter/tiffdss/releases/download/${TIFFDSS_VERSION}/tiffdss_ubuntu-latest_${TIFFDSS_VERSION}.tar.gz ${PACKAGER}/

RUN tar -zxvf tiffdss_ubuntu-latest_${TIFFDSS_VERSION}.tar.gz \
    && mv libtiffdss.so /usr/lib/ \
    && mv tiffdss /usr/local/bin/ \
    && rm -f tiffdss* utils.o

# packager and run it
COPY ./packager.py ./

USER ${USERNAME}:${USERNAME}

ENTRYPOINT ["python3", "packager.py"]
