DC = docker-compose


.PHONY: help run down destroy stop restart ps test migrate makemigrations csu run_all

help:
	@echo "Available commands:"
	@echo "  run all           - Start all containers in detached mode"
	@echo "  down              - Stop and remove containers"
	@echo "  destroy           - Stop and remove containers, networks, volumes"
	@echo "  stop              - Stop running containers"
	@echo "  restart           - Restart containers"
	@echo "  ps                - List containers"
	@echo "  test              - Run tests"
	@echo "  run               - Run FastAPI application locally"

run_all:
	${DC} up -d

run:
	 uvicorn app.main:app --reload --loop uvloop --http httptools

down:
	${DC} down

destroy:
	${DC} down -v

stop:
	${DC} stop

restart:
	${DC} restart

ps:
	${DC} ps

test:
	pytest