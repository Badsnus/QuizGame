FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt


COPY . .


ENV APP_PORT=8000

EXPOSE $APP_PORT