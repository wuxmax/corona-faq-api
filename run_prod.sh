#!/bin/bash

set -e

source .env

# docker-compose
docker-compose -f docker-compose.prod.yml -p $PROJECT_NAME up -d --build