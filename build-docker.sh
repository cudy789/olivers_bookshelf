#!/bin/bash

# Corey Knutson, April 2022

if [ "$1" = "push" ]; then
	    docker push rogueraptor7/olivers-bookshelf:1.0
else
  docker build -t rogueraptor7/olivers-bookshelf:1.0 .
fi