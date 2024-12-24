# Use Alpine as the base image
FROM alpine:latest

# Install git, python3, py3-pip, and dependencies for creating a virtual environment
RUN apk update && \
    apk add --no-cache git python3 py3-pip python3-dev libffi-dev gcc musl-dev

# Set the working directory
WORKDIR /app

# Configure git to recognize the .data directory as safe
RUN git config --global --add safe.directory /app/.data

# Install dependencies for Python packages and git
RUN apk add --no-cache git \
    && python3 -m venv venv  # Create a virtual environment

# Activate the virtual environment and install dependencies
RUN venv/bin/pip install --no-cache-dir GitPython matplotlib seaborn

# Make sure the virtual environment is used in the default shell
ENV PATH="/app/venv/bin:$PATH"