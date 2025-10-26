

DC = docker-compose
PYTEST = pytest
UVICORN = uvicorn

.PHONY: run up down test help

help:
	@echo "Available commands:"
	@echo "  run    - Run project locally"
	@echo "  up     - Run docker compose in detached mode"
	@echo "  down   - Stop docker containers"
	@echo "  test   - Run pytest"

run:
	uvicorn app.main:app --reload --loop uvloop --http httptools

up:
	$(DC) up -d

down:
	$(DC) down

test:
	$(PYTEST)