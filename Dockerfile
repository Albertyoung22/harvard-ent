FROM python:3.11-slim

WORKDIR /app

# Install essential dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full application code
COPY . .

# Set environment
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Start using Waitress production multi-threaded WSGI server
CMD ["sh", "-c", "waitress-serve --host=0.0.0.0 --port=${PORT:-5000} --threads=8 app:app"]
