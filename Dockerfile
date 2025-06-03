FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# Added git for VCS capabilities if needed during build or by dependencies
# Added curl for downloading files if necessary
# Added build-essential for C/C++ extensions that some Python packages might need
# software-properties-common is often needed for add-apt-repository, though not used here directly
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
# --no-cache-dir reduces image size
# Consider using a virtual environment inside Docker for better isolation, though not strictly necessary for all cases
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the WORKDIR
COPY . .

# Create necessary directories that the application might expect
# Example: for ChromaDB persistent storage if used locally within the container (not recommended for production)
RUN mkdir -p /app/data/chromadb

# Expose the port the app runs on (as defined in main.py and api/server.py)
EXPOSE 8000

# Define environment variable for the API Key if needed directly by the app
# ENV API_KEY="your-secret-api-key-from-dockerfile" # Better to set this in docker-compose.yml

# Command to run the application using main.py in API mode
# This assumes main.py is configured to start the FastAPI server in API mode
CMD ["python", "main.py", "--mode", "api"] 