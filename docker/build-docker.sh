#!/bin/bash

# Corey Knutson, April 2022

if [ "$1" = "build-push" ]; then
	    docker build --push --platform linux/amd64 --tag rogueraptor7/olivers-library:1.0 .
fi

docker build -t rogueraptor7/olivers-library:1.0 .

