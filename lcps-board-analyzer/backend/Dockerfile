FROM python:3.11-slim

WORKDIR /app

# System deps for pdfplumber / lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run the FastAPI web server
# Override with CMD in docker-compose.yml for the pipeline worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
