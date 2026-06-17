COMPOSE_FILE	= srcs/docker-compose.yml
DATA_DIR		= /home/omischle/data

.PHONY: all up build down stop start re clean fclean logs ps

all: up

up:
	mkdir -p $(DATA_DIR)/db $(DATA_DIR)/wp
	docker compose -f $(COMPOSE_FILE) up -d --build

build:
	mkdir -p $(DATA_DIR)/db $(DATA_DIR)/wp
	docker compose -f $(COMPOSE_FILE) build

down:
	docker compose -f $(COMPOSE_FILE) down

stop:
	docker compose -f $(COMPOSE_FILE) stop

start:
	docker compose -f $(COMPOSE_FILE) start

re: clean up

clean:
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans

fclean:
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -af
	sudo rm -rf $(DATA_DIR)

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -f $(COMPOSE_FILE) ps
