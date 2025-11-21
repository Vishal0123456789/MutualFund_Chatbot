FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with increased timeout and retries
RUN pip install --no-cache-dir --default-timeout=1000 --retries 5 -r requirements.txt

# Copy application
COPY . .

# Pre-download the sentence-transformers model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Expose port
EXPOSE 5000

# Run gunicorn with increased timeout
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "--workers", "1", "--threads", "4", "wsgi:app"]
