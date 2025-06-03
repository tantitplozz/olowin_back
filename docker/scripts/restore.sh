#!/bin/bash

# Check if backup directory is provided
if [ -z "$1" ]; then
    echo "Please provide backup directory path"
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

BACKUP_DIR=$1

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Stop services
echo "Stopping services..."
docker-compose down

# Restore MongoDB
if [ -f "$BACKUP_DIR/mongodb.archive" ]; then
    echo "Restoring MongoDB..."
    docker-compose up -d mongodb
    sleep 10  # Wait for MongoDB to start
    docker-compose exec -T mongodb mongorestore --archive < "$BACKUP_DIR/mongodb.archive"
fi

# Restore ChromaDB
if [ -f "$BACKUP_DIR/chromadb.tar.gz" ]; then
    echo "Restoring ChromaDB..."
    docker-compose up -d chromadb
    sleep 5  # Wait for ChromaDB to start
    docker-compose exec -T chromadb sh -c "rm -rf /chroma/data/* && tar xzf - -C /chroma/data" < "$BACKUP_DIR/chromadb.tar.gz"
fi

# Restore Ollama models
if [ -f "$BACKUP_DIR/ollama.tar.gz" ]; then
    echo "Restoring Ollama models..."
    docker-compose up -d ollama
    sleep 5  # Wait for Ollama to start
    docker-compose exec -T ollama sh -c "rm -rf /root/.ollama/* && tar xzf - -C /root/.ollama" < "$BACKUP_DIR/ollama.tar.gz"
fi

# Restore environment variables
if [ -f "$BACKUP_DIR/.env.backup" ]; then
    echo "Restoring environment variables..."
    cp "$BACKUP_DIR/.env.backup" ../.env
fi

# Start all services
echo "Starting all services..."
docker-compose up -d

echo "Restore completed successfully from $BACKUP_DIR" 