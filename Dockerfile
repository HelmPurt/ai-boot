# Use official slim Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Set Debian mirrors for improved reliability , because masiv problem by gcc-12
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc-12 \
        build-essential \
        cmake \
        python3-dev \
        curl \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set default GCC version workaround by this masiv problem. gcc-12 is not reliabile. download problem
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 120

# Copy requirements.txt into current working dir inside the container
# keep in mind on container is the working-dir --> WORKDIR /app 
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose FastAPI port
EXPOSE 5001

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
