FROM python:3.10.8-slim-buster

# Update the package list and install required dependencies
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    gcc libffi-dev musl-dev ffmpeg aria2 python3-pip curl \
    # Install the missing libraries required by Playwright
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and its dependencies
RUN pip3 install playwright
RUN python -m playwright install

# Copy the application files into the Docker image
COPY . /app/

# Set the working directory
WORKDIR /app/

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Expose the port (if needed)
EXPOSE 8000

# Command to start the application using Gunicorn and Python
CMD gunicorn app:app & python3 main.py
