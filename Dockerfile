FROM python:3.10.8-slim-buster
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    gcc libffi-dev musl-dev ffmpeg aria2 python3-pip curl \
    libnss3 libnssutil3 libsmime3 libnspr4 libatk-1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
RUN pip3 install playwright
RUN python -m playwright install
CMD gunicorn app:app & python3 main.py
