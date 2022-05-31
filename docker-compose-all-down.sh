#!/bin/bash
cd docker-neo4j
docker-compose down
sleep 3
cd ..
cd docker-postgres
docker-compose down
sleep 3
cd ..
cd docker-redis
docker-compose down
sleep 3
cd ..

cd docker-mongodb
docker-compose down
sleep 15