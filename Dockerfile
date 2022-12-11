FROM python

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . .

ENV APP_PORT=8000
ENV DJANGO_SECRET_KEY=top_secret_key_here
ENV DJANGO_DEBUG=true
ENV DJANGO_LANGUAGE=ru-ru

EXPOSE $APP_PORT

CMD ["python", "PyTeacher/manage.py", "runserver"]
