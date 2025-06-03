#!/bin/bash

# Create .env file if not exists
if [ ! -f ../.env ]; then
    cat > ../.env << EOL
# MongoDB
MONGO_USER=admin
MONGO_PASSWORD=$(openssl rand -base64 32)
MONGODB_URI=mongodb://admin:\${MONGO_PASSWORD}@mongodb:27017/app

# JWT
JWT_SECRET_KEY=$(openssl rand -base64 32)

# API URLs
BACKEND_URL=http://localhost:8000
WS_URL=ws://localhost:8000/ws

# Environment
ENVIRONMENT=production
NODE_ENV=production

# Optional: GPU settings for Ollama
NVIDIA_VISIBLE_DEVICES=all
EOL
    echo "Created .env file with secure random passwords"
fi

# Create data directories
mkdir -p ../data/mongodb
mkdir -p ../data/chromadb
mkdir -p ../data/ollama

# Set correct permissions
chmod 600 ../.env
chmod 700 ../data/mongodb
chmod 700 ../data/chromadb
chmod 700 ../data/ollama

echo "Initialization complete. Please review the .env file and modify if needed." 