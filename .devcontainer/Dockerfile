FROM mcr.microsoft.com/vscode/devcontainers/python:3.9

# Install PostgreSQL client
RUN apt-get update && \
    apt-get install -y postgresql-client

# Set the working directory
WORKDIR /workspace

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt
