
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# builder
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
FROM python:3.12-alpine AS builder
ARG TEST_DATA_TAG

ENV PATH=/opt/geoproc/venv/bin:$PATH

ENV GEOPROC=/opt/geoproc

RUN apk update

WORKDIR ${GEOPROC}

ADD https://github.com/USACE/cumulus-geoproc-test-data/releases/download/${TEST_DATA_TAG}/cumulus-geoproc-test-data.tar.gz ${GEOPROC}

RUN tar -xzvf cumulus-geoproc-test-data.tar.gz && \
    rm -f cumulus-geoproc-test-data.tar.gz

RUN python -m venv ${GEOPROC}/venv \
    && . activate \
    && pip install boto3 requests httpx httpx[http2]

COPY ./products.py ./

ENTRYPOINT [ "python3", "products.py" ]
