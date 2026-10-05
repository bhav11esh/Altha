.PHONY: help up down build rebuild logs logs-crewai logs-conversation logs-api logs-ui clean stop start restart ps shell-crewai shell-conversation shell-api shell-postgres shell-redis test lint

# Default target
help:
	@echo "MediAI Docker Commands"
	@echo "======================="
	@echo ""
	@echo "Setup & Deployment:"
	@echo "  make up               - Start all services"
	@echo "  make down             - Stop and remove containers"
	@echo "  make build            - Build all services"
	@echo "  make rebuild          - Rebuild all services from scratch"
	@echo "  make restart          - Restart all services"
	@echo ""
	@echo "Management:"
	@echo "  make ps               - Show running containers"
	@echo "  make stop             - Stop services without removing"
	@echo "  make start            - Start stopped services"
	@echo "  make clean            - Remove all containers and volumes"
	@echo ""
	@echo "Logs:"
	@echo "  make logs             - View all service logs"
	@echo "  make logs-crewai      - View CrewAI logs"
	@echo "  make logs-conversation - View Conversation Service logs"
	@echo "  make logs-api         - View API Integration logs"
	@echo "  make logs-ui          - View OpenWebUI logs"
	@echo ""
	@echo "Shell Access:"
	@echo "  make shell-crewai     - Access CrewAI service shell"
	@echo "  make shell-conversation - Access Conversation Service shell"
	@echo "  make shell-api        - Access API Integration shell"
	@echo "  make shell-postgres   - Access PostgreSQL CLI"
	@echo "  make shell-redis      - Access Redis CLI"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make health           - Check service health"
	@echo ""

# Setup and Deployment
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Integration: http://localhost:8003"

down:
	@echo "Stopping and removing services..."
	docker-compose down

build:
	@echo "Building services..."
	docker-compose build

rebuild:
	@echo "Rebuilding all services from scratch..."
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

restart:
	@echo "Restarting services..."
	docker-compose restart

# Management
ps:
	@echo "Running containers:"
	docker-compose ps

stop:
	@echo "Stopping services..."
	docker-compose stop

start:
	@echo "Starting services..."
	docker-compose start

clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "Cleanup complete!"

# Logs
logs:
	docker-compose logs -f --tail=100

logs-crewai:
	docker-compose logs -f --tail=50 crewai

logs-conversation:
	docker-compose logs -f --tail=50 conversation-service

logs-api:
	docker-compose logs -f --tail=50 api-integration

logs-ui:
	docker-compose logs -f --tail=50 openwebui

# Shell Access
shell-crewai:
	docker-compose exec crewai bash

shell-conversation:
	docker-compose exec conversation-service bash

shell-api:
	docker-compose exec api-integration bash

shell-postgres:
	docker-compose exec postgres psql -U mediai -d mediai

shell-redis:
	docker-compose exec redis redis-cli

# Testing & Health
health:
	@echo "Checking service health..."
	@echo ""
	@echo "CrewAI (8001):"
	@curl -s http://localhost:8001/health | jq . || echo "Not responding"
	@echo ""
	@echo "Conversation Service (8002):"
	@curl -s http://localhost:8002/health | jq . || echo "Not responding"
	@echo ""
	@echo "API Integration (8003):"
	@curl -s http://localhost:8003/health | jq . || echo "Not responding"
	@echo ""
	@echo "OpenWebUI (3000):"
	@curl -s http://localhost:3000/health | jq . || echo "Not responding"
	@echo ""
	@echo "Database (PostgreSQL):"
	@docker-compose exec -T postgres pg_isready -U mediai || echo "Not responding"
	@echo ""
	@echo "Cache (Redis):"
	@docker-compose exec -T redis redis-cli ping || echo "Not responding"
	@echo ""

test:
	@echo "Running tests..."
	@echo "Note: Implement service-specific tests"

lint:
	@echo "Linting Python services..."
	@echo "Note: Add linting configuration"

# Utility
version:
	@echo "Docker version:"
	docker --version
	@echo ""
	@echo "Docker Compose version:"
	docker-compose --version

stats:
	@echo "Container resource usage:"
	docker stats --no-stream mediai-*

env-setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from .env.example"; \
		echo "Please review and update credentials in .env"; \
	else \
		echo ".env file already exists"; \
	fi

backup-data:
	@echo "Backing up database..."
	docker-compose exec -T postgres pg_dump -U mediai mediai > mediai_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup complete!"

reset-db:
	@echo "WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		echo "Database reset complete!"; \
	else \
		echo "Cancelled."; \
	fi

install-tools:
	@echo "Installing development tools..."
	@command -v docker >/dev/null 2>&1 || echo "Please install Docker"
	@command -v docker-compose >/dev/null 2>&1 || echo "Please install Docker Compose"
	@echo "Tools check complete!"
