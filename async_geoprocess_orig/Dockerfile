FROM osgeo/gdal

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
  && apt-get install -y python3-pip

COPY requirements*.txt ./
RUN \
    pip3 install -r requirements-pre.txt; \
    pip3 install -r requirements.txt

# Copy, build, install cumulus
COPY ./cumulus ./cumulus
RUN cd cumulus \
 && pip3 install wheel \
 && python3 setup.py bdist_wheel \
 && pip3 install dist/snodas-0.0.1-py3-none-any.whl \
 && cd ../ \
 && rm -rf ./cumulus

# Copy, build, install geoprocess
RUN mkdir /app
COPY geoprocess_worker /app/geoprocess_worker
WORKDIR /app/geoprocess_worker

CMD python3 worker.py