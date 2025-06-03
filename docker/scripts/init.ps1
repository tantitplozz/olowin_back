# Create .env file if not exists
if (-not (Test-Path -Path "../.env")) {
    @"
# MongoDB
MONGO_USER=admin
MONGO_PASSWORD=$(New-Guid)
MONGODB_URI=mongodb://admin:`${MONGO_PASSWORD}@mongodb:27017/app

# JWT
JWT_SECRET_KEY=$(New-Guid)

# API URLs
BACKEND_URL=http://localhost:8000
WS_URL=ws://localhost:8000/ws

# Environment
ENVIRONMENT=production
NODE_ENV=production

# Optional: GPU settings for Ollama
NVIDIA_VISIBLE_DEVICES=all
"@ | Set-Content -Path "../.env"
    Write-Host "Created .env file with secure random values"
}

# Create data directories
New-Item -ItemType Directory -Force -Path "../data/mongodb"
New-Item -ItemType Directory -Force -Path "../data/chromadb"
New-Item -ItemType Directory -Force -Path "../data/ollama"

Write-Host "Initialization complete. Please review the .env file and modify if needed." 