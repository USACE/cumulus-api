FROM osgeo/gdal

ARG HOST_WORKING_DIRECTORY

ARG LOGGER_LEVEL=2

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/$HOST_WORKING_DIRECTORY

ENV HOME /app/$HOST_WORKING_DIRECTORY

WORKDIR $HOME

ENV PATH $HOME/bin:$HOME/local/bin:$PATH

COPY . .

# pip install/upgrade requirements before the cumulus package
RUN python3 -m pip install --upgrade pip wheel setuptools \
  && python3 -m pip install $HOME/

CMD ["python3", "start_worker.py"]
