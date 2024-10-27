#!/bin/bash

# Define variables
IMAGE_NAME="python:3.12"   # Change this if you need a specific version of Python
CONTAINER_NAME="python_container"
LOCAL_VOLUME_PATH="."
CONTAINER_VOLUME_PATH="/root"   # Path inside the container

# Step 1: Pull the Python Docker image
echo "Pulling Docker image $IMAGE_NAME..."
docker pull $IMAGE_NAME

# Step 2: Run the Docker container with the volume
echo "Starting Docker container with the volume mounted..."
docker run -d --name $CONTAINER_NAME -v "$LOCAL_VOLUME_PATH:$CONTAINER_VOLUME_PATH" -w "$CONTAINER_VOLUME_PATH" $IMAGE_NAME tail -f /dev/null

# Step 3: Install the Python packages from requirements.txt
echo "Installing requirements from requirements.txt..."
docker exec $CONTAINER_NAME pip install -r "$CONTAINER_VOLUME_PATH/requirements.txt"

echo "Setup complete. The container $CONTAINER_NAME is running with the specified volume mounted."

