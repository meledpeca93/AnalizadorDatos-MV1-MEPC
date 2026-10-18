#!/bin/sh
set -eu
mkdir -p evidence
docker compose exec -T web python --version > evidence/python-container.txt
docker compose exec -T web python manage.py test --verbosity 2 > evidence/tests-docker.txt 2>&1
docker compose ps > evidence/compose-ps.txt
container_id=$(docker compose ps -q web)
docker stats --no-stream "$container_id" > evidence/docker-stats.txt
docker inspect --format 'Memory={{.HostConfig.Memory}} NanoCpus={{.HostConfig.NanoCpus}}' "$container_id" > evidence/docker-limits.txt
date -u '+%Y-%m-%dT%H:%M:%SZ' > evidence/captured-at.txt
