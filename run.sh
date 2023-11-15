#!/bin/bash

(
    cd app || exit 1
    while true; do
        uvicorn main:app
        echo "------------------------"
        echo "starting again..."
        echo "------------------------"
        sleep 3
    done
)
