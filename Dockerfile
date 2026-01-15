FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if any (none obvious from requirements, but good practice to clean apt)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY bot.py .
COPY search/ ./search/
COPY json/ ./json/
COPY functions/ ./functions/

# Create log directory
RUN mkdir -p log

CMD ["python", "bot.py"]
