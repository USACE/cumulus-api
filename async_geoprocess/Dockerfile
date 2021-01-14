FROM osgeo/gdal

ENV PYTHONUNBUFFERED=1

RUN apt-get -y update \
  && apt-get install -y python3-pip

RUN pip3 install --no-cache-dir boto3 psycopg2-binary requests

# Copy, build, install cumulus dependencies
COPY ./cumulus ./cumulus
RUN cd cumulus \
 && pip3 install wheel \
 && python3 setup.py bdist_wheel \
 && pip3 install dist/snodas-0.0.1-py3-none-any.whl \
 && cd ../ \
 && rm -rf ./cumulus

# Message Handler
RUN mkdir /app

WORKDIR /app

COPY sqs_handler.py /app/sqs_handler.py

CMD python3 sqs_handler.py
