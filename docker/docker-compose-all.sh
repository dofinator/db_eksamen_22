#!/bin/bash
cd docker-neo4j
docker-compose up -d
sleep 3
cd ..
cd docker-postgres
docker-compose up -d
sleep 3
cd ..
cd docker-redis
docker-compose up -d
sleep 3
cd ..

cd docker-mongodb
docker-compose up -d
