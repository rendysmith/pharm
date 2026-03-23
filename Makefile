.PHONY: help build push run stop logs clean deploy-local

# ====================== НАСТРОЙКИ ======================
DOCKER_USERNAME ?= rendysmith3000
IMAGE_NAME      ?= pharm-bot
TAG             ?= latest

# ====================== КОМАНДЫ ======================

help: ## Показать все доступные команды
	@echo "Используйте 'make <target>' где <target> это одно из:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образ
	docker build -t $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG) .

push: build ## Собрать и запушить образ в Docker Hub
	docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

run: ## Запустить локально (для разработки)
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/service_account.json:/app/service_account.json \
		-v $(PWD)/utils:/app/utils \
		$(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

logs: ## Посмотреть логи контейнера на сервере
	ssh root@xxx.xxx.xxx.xxx 'docker logs pharm-bot --tail 100 -f'   # ← замени на свой IP

stop: ## Остановить контейнер на сервере
	ssh root@xxx.xxx.xxx.xxx 'docker stop pharm-bot || true'

clean: ## Очистка неиспользуемых образов и контейнеров
	docker system prune -f

# ====================== ДЕПЛОЙ ======================
deploy-local: ## Деплой вручную через SSH (если нужно)
	@echo "Деплой на сервер..."
	ssh root@xxx.xxx.xxx.xxx 'cd ~/pharm && \
		docker pull $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG) && \
		docker stop pharm-bot || true && \
		docker rm pharm-bot || true && \
		docker run -d \
			--name pharm-bot \
			--restart unless-stopped \
			--env-file .env \
			-v $$(pwd)/service_account.json:/app/service_account.json \
			-v $$(pwd)/utils:/app/utils \
			$(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)'