COMPOSE = docker compose -f infra/docker-compose.yml --env-file infra/.env

.PHONY: env up up-llm down ps logs check reset-db

env:            ## create infra/.env from the example (first run only)
	@test -f infra/.env || cp infra/.env.example infra/.env

up: env         ## start postgres, redis, mailpit, langfuse
	$(COMPOSE) up -d

up-llm: env     ## same + ollama in Docker
	$(COMPOSE) --profile local-llm up -d

down:
	$(COMPOSE) down

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f --tail=100

check:          ## Day 1 done-when check
	python scripts/check_stack.py

reset-db:       ## wipe all data volumes (asks no questions!)
	$(COMPOSE) down -v
