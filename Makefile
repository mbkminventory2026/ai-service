APP_NAME := permatatex-ai-service
CONTAINER_NAME := ai-service-container
PORT := 8000

.PHONY: dev docker-up docker-down docker-logs clean

dev:
	uvicorn main:app --reload --port $(PORT)

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

clean: docker-down
	-docker rmi $(APP_NAME)
