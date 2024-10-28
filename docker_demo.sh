#!/bin/bash

# Define variables
IMAGE_NAME="quran_root_docker"
CONTAINER_NAME="quran_root_container"
LOCAL_VOLUME_PATH="."
CONTAINER_VOLUME_PATH="/root"   # Path inside the container

# Step 1: Check if the Docker image already exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  echo "Docker image $IMAGE_NAME not found. Building the image..."
  docker build -t $IMAGE_NAME .
else
  echo "Docker image $IMAGE_NAME already exists. Skipping build step."
fi

# Step 2: Run the Docker container interactively with volume mounting
echo "Starting Docker container interactively..."
docker run --rm -it --name $CONTAINER_NAME -v "$LOCAL_VOLUME_PATH:$CONTAINER_VOLUME_PATH" -w "$CONTAINER_VOLUME_PATH" $IMAGE_NAME /bin/bash
