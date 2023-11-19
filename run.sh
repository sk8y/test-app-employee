#!/bin/bash

(
    export REDIS_URL=redis://127.0.0.1:6379
    cd app || exit 1
    while true; do
        uvicorn main:app
        echo "------------------------"
        echo "starting again..."
        echo "------------------------"
        sleep 3
    done
)
