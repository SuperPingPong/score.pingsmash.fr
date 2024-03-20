#!/bin/bash

rm ../backend/ranks.json
python3 main.py

cd ..
#  source .env
#  docker-compose build api --no-cache
#  docker-compose up -d
docker cp backend/ranks.json scorepingsmashfr_api_1:/app/ranks.json
docker-compose restart api
cd -
