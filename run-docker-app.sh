#!/bin/bash

# Corey Knutson April 2022

if [ "$1" = "" ]; then
	DT="1.0"
  else
	DT=$1
fi

docker run --rm -h olivers-bookshelf --volume="/mnt/user/keys/olivers-bookshelf:/key/" -p 5000:5000 -it rogueraptor7/olivers-bookshelf:$DT
