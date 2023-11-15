#!/bin/bash

docker rm -f test-app-employee-redis
docker run -it --name test-app-employee-redis -p 6379:6379 redis/redis-stack-server:latest
docker rm -f test-app-employee-redis
