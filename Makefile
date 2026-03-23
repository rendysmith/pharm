.PHONY: build push deploy logs stop clean

# Переменные
DOCKER_USERNAME = rendysmith3000
IMAGE_NAME = pharm-bot
SERVER_HOST = 68807
SERVER_USER = root

build:
	docker build -t $(DOCKER_USERNAME)/$(IMAGE_NAME):latest .

push:
	docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):latest

deploy:
	@echo "Деплой на сервер $(SERVER_HOST)..."
	ssh $(SERVER_USER)@$(SERVER_HOST) 'cd ~/pharm && \
		docker pull $(DOCKER_USERNAME)/$(IMAGE_NAME):latest && \
		docker stop pharm-bot || true && \
		docker rm pharm-bot || true && \
		docker run -d \
			--name pharm-bot \
			--restart unless-stopped \
			--env-file .env \
			-v $$(pwd)/service_account.json:/app/service_account.json \
			-v $$(pwd)/utils:/app/utils \
			$(DOCKER_USERNAME)/$(IMAGE_NAME):latest'

logs:
	ssh $(SERVER_USER)@$(SERVER_HOST) 'docker logs pharm-bot --tail 50 -f'

stop:
	ssh $(SERVER_USER)@$(SERVER_HOST) 'docker stop pharm-bot || true'

clean:
	ssh $(SERVER_USER)@$(SERVER_HOST) 'docker system prune -f'