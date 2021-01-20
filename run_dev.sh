#!/bin/sh

set -e

source .env

# docker-compose
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME up -d --build

# follow api container logs
docker logs -f ${PROJECT_NAME}_api_1