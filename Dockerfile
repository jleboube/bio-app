# Use official Python base image
FROM python:3.9-slim

# Install Tkinter dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    tcl-dev \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY ./app/ .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set entrypoint
CMD ["python", "main.py"]