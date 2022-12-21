# Makefile

.PHONY: build
build:
	docker compose build

.PHONY: run
run:
	docker compose run app

.PHONY: format
format:
	black src
	isort src
