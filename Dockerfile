FROM python

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . .

EXPOSE $APP_PORT

CMD ["python", "PyTeacher/manage.py", "runserver"]
