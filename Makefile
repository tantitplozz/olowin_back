.PHONY: help dev-backend dev-frontend build up down test clean monitoring

SHELL := /bin/bash

help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-deps-backend: ## Install backend dependencies
	cd backend && pip install -r requirements/ai.txt -r requirements/db.txt

install-deps-frontend: ## Install frontend dependencies
	cd frontend && npm install

dev-backend: ## Run backend in development mode
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: down up ## Restart all services

logs: ## Show logs
	docker-compose logs -f

monitoring-up: ## Start monitoring stack
	cd monitoring && docker-compose up -d

monitoring-down: ## Stop monitoring stack
	cd monitoring && docker-compose down

test: ## Run tests
	cd backend && pytest

clean: ## Clean up
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +

setup-dev: install-deps-backend install-deps-frontend ## Setup development environment 