FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt


COPY . .

#RUN python quiz/manage.py migrate
#RUN python quiz/manage.py collectstatic

ENV APP_PORT=8000

EXPOSE $APP_PORT