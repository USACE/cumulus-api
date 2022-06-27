FROM osgeo/gdal:ubuntu-small-3.5.0

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

ENV PACKAGE=async_geoprocess

RUN mkdir -p /app/${PACKAGE}

WORKDIR /app/${PACKAGE}

COPY . .

# pip install/upgrade requirements before the cumulus package
# sphinx used to generate documentation from docstrings
RUN python3 -m pip install --upgrade pip wheel setuptools && \
    python3 -m pip install /app/${PACKAGE}/ Sphinx sphinx_rtd_theme

RUN useradd appuser && \
    mkdir -p -m 775 docs && \
    chown appuser:appuser docs

USER appuser

CMD ["python3", "worker.py"]
