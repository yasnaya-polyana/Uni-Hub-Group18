FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . . 