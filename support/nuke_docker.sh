#!/bin/bash

# Stop/Remove All Docker Containers
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

# Remove All Docker Images
docker image rm $(docker image ls -a -q)
