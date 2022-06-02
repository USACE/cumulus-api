# Compile DSS
FROM ubuntu:18.04 AS cbuilder

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y gcc gfortran zlib1g-dev make git && \
    rm -rf /var/lib/apt/lists/*

RUN git clone -b master --single-branch https://github.com/HydrologicEngineeringCenter/hec-dss.git

COPY Makefile /

RUN make

#
FROM osgeo/gdal:ubuntu-small-3.4.3 as packager

# force stdout and stderr to be unbuffered setting to non-empty
ENV PYTHONUNBUFFERED=1

ENV PACKAGE=async_packager

# update, install and clean up
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y gcc gfortran python3-pip && \
    rm -rf /var/lib/apt/lists/*


COPY --from=cbuilder --chown=root:root /hec-dss/heclib/heclib_c/Output/libhec_c.a /usr/lib/
COPY --from=cbuilder --chown=root:root /hec-dss/heclib/heclib_f/Output/libhec_f.a /usr/lib/
COPY --from=cbuilder --chown=root:root /hec-dss/heclib/heclib_c/src/headers /hec-dss/heclib/heclib_c/src/headers

RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

RUN bash ./tiffdss/src/make.sh

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install /app/${PACKAGE}/



# # RUN mkdir /app /output

# # WORKDIR /
# # COPY packager/requirements.txt ./
# # RUN pip3 install --no-cache-dir -r requirements.txt --upgrade
# # RUN rm requirements.txt

# # COPY packager /app/packager
# # WORKDIR /app/packager

# # RUN useradd appuser
# # USER appuser

CMD python3 packager.py
# CMD [ "tail", "-f" , "/dev/null" ]
