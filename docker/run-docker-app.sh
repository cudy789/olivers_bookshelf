#!/bin/bash

# Corey Knutson April 2022

if [ "$1" = "" ]; then
	DT="1.0"
  else
	DT=$1
fi
  

docker run --rm -h olivers-library --network host $@ -it rogueraptor7/olivers-library:$DT
