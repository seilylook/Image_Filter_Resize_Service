.PHONY: _requirements build start stop clean test

IMAGE_NAME=server
DEFAULT_TAG=latest

_requirements:
	@echo "=============================================="
	@echo "Exporting Python dependencies to requirements.txt..."
	@echo "=============================================="
	poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev
	@echo "\n"

build: _requirements
	@echo "=============================================="
	@echo "Building Docker image $(IMAGE_NAME):$(DEFAULT_TAG)..."
	@echo "=============================================="
	docker build -t $(IMAGE_NAME):$(DEFAULT_TAG) .
	@echo "\n"

