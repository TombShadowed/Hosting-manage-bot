FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git build-essential libssl-dev libffi-dev python3-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN mkdir -p /mnt/data/bots
ENV BASE_DATA_DIR=/mnt/data/bots
CMD ["python", "main.py"]
