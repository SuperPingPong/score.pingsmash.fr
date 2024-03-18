#!/bin/bash

rm ../backend/ranks.json
python3 main.py

cd ..
source .env
docker-compose build
docker-compose up -d
cd -
