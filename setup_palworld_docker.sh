#!/bin/bash
# This script assume you have docker and docker compose plugins installed

# Define the directory to store the docker-compose file
DIR="/root/palworld"

# Creating the directory
mkdir -p "$DIR"

# Navigate to the directory
cd "$DIR"

# Docker Compose content
DOCKER_COMPOSE_YAML=$(cat <<EOF
version: '3.8'

services:
   palworld:
      image: thijsvanloef/palworld-server-docker:latest
      restart: unless-stopped
      container_name: palworld-server
      stop_grace_period: 30s # Set to however long you are willing to wait for the container to gracefully stop
      ports:
        - 8211:8211/udp
        - 27015:27015/udp
      environment:
         - PUID=1000
         - PGID=1000
         - PORT=8211 # Optional but recommended
         - PLAYERS=16 # Optional but recommended
         - SERVER_PASSWORD="xiaofei" # Optional but recommended
         - MULTITHREADING=true
         - RCON_ENABLED=true
         - RCON_PORT=25575
         - TZ=UTC
         - ADMIN_PASSWORD="biegaowo"
         - COMMUNITY=false  # Enable this if you want your server to show up in the community servers tab, USE WITH SERVER_PASSWORD!
         - SERVER_NAME="帕鲁黑奴种植园"
         - SERVER_DESCRIPTION="帕鲁黑奴种植园"
      volumes:
         - ./palworld:/palworld/
EOF
)

# Write the Docker Compose content to a file
echo "$DOCKER_COMPOSE_YAML" > docker-compose.yml

# Run Docker Compose
docker-compose up -d