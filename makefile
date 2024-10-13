# Makefile for Docker Compose

.PHONY: build up down

# Build the Docker images
build:
	docker-compose up --build -d

# Start the containers in the background
up:
	docker-compose up -d

# Stop and remove the containers
down:
	docker-compose down
