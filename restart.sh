#!/bin/sh
git pull
git log --oneline -n 1
docker compose down
docker compose up --build -d