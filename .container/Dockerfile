FROM python:3.12.6-slim

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Add where UV installs itself to the system PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install basic system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    bash \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Debug: list contents of the scripts folder
RUN ls -la ./scripts

# Ensure the setup script is executable
RUN chmod +x ./scripts/setup_dev_env.sh

# Run your setup script using bash
RUN bash ./scripts/setup_dev_env.sh

# Default command when the container starts
CMD ["bash"]
