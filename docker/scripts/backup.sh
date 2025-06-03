#!/bin/bash

# Set backup directory
BACKUP_DIR="../backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup MongoDB
echo "Backing up MongoDB..."
docker-compose exec -T mongodb mongodump --archive > "$BACKUP_DIR/mongodb.archive"

# Backup ChromaDB
echo "Backing up ChromaDB..."
docker-compose exec -T chromadb tar czf - /chroma/data > "$BACKUP_DIR/chromadb.tar.gz"

# Backup Ollama models
echo "Backing up Ollama models..."
docker-compose exec -T ollama tar czf - /root/.ollama > "$BACKUP_DIR/ollama.tar.gz"

# Backup environment variables
echo "Backing up environment variables..."
cp ../.env "$BACKUP_DIR/.env.backup"

# Create backup info file
cat > "$BACKUP_DIR/backup_info.txt" << EOL
Backup created on: $(date)
Docker compose version: $(docker-compose version --short)
Services backed up:
- MongoDB
- ChromaDB
- Ollama
- Environment variables
EOL

echo "Backup completed successfully to $BACKUP_DIR" 