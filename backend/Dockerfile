FROM python:3.13-bookworm

WORKDIR /app

# Install system dependencies + CA certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
        git \
        ca-certificates \
        openssl \
        libssl-dev \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Force Python to use system certs (works for requests/urllib3/transformers)
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt

# Upgrade pip, setuptools, wheel, certifi
RUN python -m ensurepip && \
    python -m pip install --upgrade pip setuptools wheel certifi

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
