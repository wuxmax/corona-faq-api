#!/bin/bash

set -e

source .env

export ES_HOST="${PROJECT_NAME}_es"
export ES_HOST_URL="http://${ES_HOST}:9200"

# docker-compose
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml -p $PROJECT_NAME up -d --build

# follow api container logs
docker logs -f ${PROJECT_NAME}_api_1