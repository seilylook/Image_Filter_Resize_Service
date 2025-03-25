.PHONY: server-build all-up restart

PROJECT_NAME=image-filter-resize-service

server-build:
	@echo "=============================================="
	@echo "Generating Python requirements files..."
	@echo "=============================================="
	$(MAKE) -C server _requirements
	@echo "✅ Requirements generated successfully"
	@echo "\n"

	@echo "=============================================="
	@echo "Building API server..."
	@echo "=============================================="
	$(MAKE) -C server build
	@echo "✅ Python server built successfully"
	@echo "\n"

all-up: server-build 
	@echo "=============================================="
	@echo "Starting all $(PROJECT_NAME) containers(Python, Spark, Kafka, Elasticsearch, Kibana, MinIO)..."
	@echo "=============================================="
	docker compose up -d
	@echo "✅ All containers(Python, Spark, Kafka, Elasticsearch, Kibana, MinIO) started successfully"
	@echo "\n"

restart:
	@echo "=============================================="
	@echo "Restart the server"
	@echo "=============================================="
	cd ./server python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload