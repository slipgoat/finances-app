#!/usr/bin/env bash
echo "Building dev..."
docker-compose up -d --build
docker image prune -a -f
count=$(docker ps -q | wc -l)
if [[ $count -ne 4 ]]; then
  echo "Only $count of 4 containers is running"
  exit 1
fi