#!/bin/bash
# build.sh

# Ensure docker can be run without sudo
if ! groups | grep -q "\bdocker\b"; then
  echo "You are not in the docker group. Please add your user to the docker group and log out/in for changes to take effect."
  exit 1
fi

# Commands to add the user to the docker group
: <<'CREATE_DOCKER_GROUP'
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
CREATE_DOCKER_GROUP

# Ensure Docker Container is stopped and removed before building
if sudo docker ps -a --format '{{.Names}}' | grep -q '^minecraft-bedrock-server$'; then
  echo "Stopping and removing existing minecraft-bedrock-server container..."
  sudo docker stop minecraft-bedrock-server
  sudo docker rm minecraft-bedrock-server
fi

# Build the Docker image
sudo docker build -t fingerhutascode/minecraft-bedrock-server:mod-loader-v1 .