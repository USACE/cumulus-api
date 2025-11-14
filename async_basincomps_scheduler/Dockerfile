FROM python:3.11-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    gdal-bin \
    libgdal-dev \
    default-jre-headless \
    ca-certificates \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install HEC-MetVue
RUN wget -O /tmp/hec-metvue.zip \
    https://www.hec.usace.army.mil/software/hec-metvue/downloads/HEC-MetVue_341_Portable.zip && \
    unzip /tmp/hec-metvue.zip -d /opt/hec-metvue && \
    rm /tmp/hec-metvue.zip && \
    # Create symlink without spaces to avoid shell quoting issues
    ln -s "/opt/hec-metvue/HEC-MetVue_341_Portable/HEC-MetVue 3.4.1" /opt/hec-metvue/metvue341

# Set HEC-MetVue environment variables (using symlink path without spaces)
ENV METVUE_EXE="/opt/hec-metvue/metvue341"
ENV PATH="${METVUE_EXE}/utilities/unix:${PATH}"

# Convert line endings from CRLF to LF (Windows to Unix)
RUN dos2unix "${METVUE_EXE}/utilities/unix/"*

# Make scripts executable
RUN chmod +x "${METVUE_EXE}/utilities/unix/"*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create config directory for shapefile
RUN mkdir -p /app/config

COPY src/ /app/src/

ENV PYTHONPATH=/app/src

# Run scheduler
CMD ["python", "-m", "basincomps_scheduler.scheduler"]
