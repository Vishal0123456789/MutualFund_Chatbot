FROM python:3.11-slim

WORKDIR /app

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files
COPY requirements.txt .
COPY scripts/ ./scripts/
COPY rag_data/ ./rag_data/
COPY wsgi.py .

# Install Python dependencies with aggressive optimization
RUN pip install --no-cache-dir --compile --default-timeout=1000 -r requirements.txt && \
    find /usr/local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local -type f -name '*.pyc' -delete

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "--workers", "1", "--max-requests", "100", "wsgi:app"]
