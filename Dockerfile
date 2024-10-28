# Dockerfile
# Specify the base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /root

# Copy requirements.txt to the container
COPY requirements.txt /root/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /root/requirements.txt

# Set up a command to keep the container running
CMD ["tail", "-f", "/dev/null"]
