FROM python:3.11-slim

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

# Copy the current directory contents into the container at /app
# This includes requirements.txt, ui_server.py, and all module folders (auth, agents, etc.)
COPY . .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories that the application might expect
# Example: for ChromaDB persistent storage if used locally within the container (not recommended for production)
RUN mkdir -p /app/data/chromadb

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variables (though these are better set in docker-compose.yml or by the orchestrator)
# ENV NAME World

# Run ui_server.py when the container launches
CMD ["uvicorn", "ui_server:app", "--host", "0.0.0.0", "--port", "8000"] 