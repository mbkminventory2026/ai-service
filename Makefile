APP_NAME := permatatex-ai-service
CONTAINER_NAME := ai-service-container
PORT := 8000

.PHONY: dev docker-up docker-down docker-logs clean

dev:
	uvicorn main:app --reload --port $(PORT)

docker-up:
	docker build -t $(APP_NAME) .
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):$(PORT) --env-file .env $(APP_NAME)

docker-down:
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)

docker-logs:
	docker logs -f $(CONTAINER_NAME)

clean: docker-down
	-docker rmi $(APP_NAME)
