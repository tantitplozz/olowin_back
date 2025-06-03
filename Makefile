.PHONY: up down frontend backend monitoring logs clean

# Docker commands
up:
	docker-compose -f frontend/docker-compose.yml -f backend/docker-compose.yml up -d

down:
	docker-compose -f frontend/docker-compose.yml -f backend/docker-compose.yml down

# Frontend commands
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend: frontend-install frontend-dev

# Backend commands
backend-install:
	cd backend && pip install -r requirements/base.txt

backend-dev:
	cd backend && uvicorn src.main:app --reload --port 8001

backend: backend-install backend-dev

# Monitoring commands
monitoring:
	docker-compose -f monitoring/docker-compose.yml up -d

# Utility commands
logs:
	docker-compose -f frontend/docker-compose.yml -f backend/docker-compose.yml logs -f

clean:
	docker-compose -f frontend/docker-compose.yml -f backend/docker-compose.yml down -v
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete 