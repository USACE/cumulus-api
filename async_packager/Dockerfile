# Compile DSS and tiffdss
FROM osgeo/gdal:ubuntu-small-3.5.0 as cbuilder

RUN apt-get -y update && \
    apt-get install -y git gcc gfortran python3-pip libffi-dev gdb zlib1g-dev make  && \
    rm -rf /var/lib/apt/lists/*

# clone the branches needed to compile
RUN git clone --branch 7-IJ --single-branch https://github.com/HydrologicEngineeringCenter/hec-dss.git
RUN git clone --branch stable --single-branch https://github.com/HydrologicEngineeringCenter/tiffdss.git

# Compile heclib C
WORKDIR /hec-dss/heclib/heclib_c
RUN make

# Compile heclib Fortran
WORKDIR /hec-dss/heclib/heclib_f
RUN make

# Environment variable in the tiffdss makefile
ENV HECFLAG="/hec-dss/heclib/heclib_c/Output/libhec_c.a /hec-dss/heclib/heclib_f/Output/libhec_f.a"

# Compile tiffdss with heclib C, heclib Fortran and GDAL library in /usr/lib
WORKDIR /tiffdss/src
RUN make libtiffdss.so

# Packager
FROM osgeo/gdal:ubuntu-small-3.5.0 as packager

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR

ENV PACKAGE=async_packager

# update, install and clean up
RUN apt-get -y update && \
    apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# pip install/upgrade requirements before the cumulus package
# sphinx used to generate documentation from docstrings
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install /app/${PACKAGE}/ Sphinx sphinx_rtd_theme

# copy over the libtiffdss.so
COPY --from=cbuilder --chown=root:root /tiffdss/src/libtiffdss.so /usr/lib/

RUN useradd appuser && \
    mkdir -p -m 775 docs && \
    chown appuser:appuser docs

USER appuser

CMD python3 packager.py
# local testing only
# CMD [ "tail", "-f" , "/dev/null" ]
