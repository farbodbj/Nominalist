
# Dockerfile
FROM focker.ir/python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --index-url https://mirror-pypi.runflare.com/simple

# Copy source code
COPY src/ ./src/

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
