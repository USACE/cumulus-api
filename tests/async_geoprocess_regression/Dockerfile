FROM osgeo/gdal:ubuntu-small-3.4.2
# ARG GIT_REPO_URL=GIT_REPO_URL
# ARG GIT_BRANCH=GIT_BRANCH

ENV PYTHONUNBUFFERED=1
ENV GIT_REPO_URL=GIT_REPO_URL
ENV GIT_BRANCH=GIT_BRANCH

RUN apt-get update -y && apt-get install -y \
  python3-pip git \
  && rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /app/async_geoprocess && git clone --branch ${GIT_BRANCH} --single-branch ${GIT_REPO_URL}
# RUN cp -r /cumulus-api/async_geoprocess/* /app/async_geoprocess && rm -r /cumulus-api

RUN mkdir -p /app/async_geoprocess

WORKDIR /app/async_geoprocess

# COPY . .
COPY *.py .
COPY setup.sh .

# pip install/upgrade requirements before the cumulus package
# RUN python3 -m pip install --upgrade pip wheel setuptools \
#   && python3 -m pip install /app/async_geoprocess/

# RUN useradd appuser
# USER appuser

# CMD ["python3", "tester.py"]
CMD ./setup.sh && python tester.py 2>&1 | tee /output/results.log
