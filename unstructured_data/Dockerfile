FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV UV_HTTP_TIMEOUT=600

# Install uv using pip
RUN pip install --no-cache-dir uv chardet tabulate

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
COPY uv.lock .


# Install Python dependencies using uv
RUN uv pip compile pyproject.toml > requirements.txt && \
    uv pip install --system -r requirements.txt
# RUN uv pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app runs on
# EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"] 