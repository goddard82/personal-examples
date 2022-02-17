FROM lkwd.jfrog.io/docker-main/python:3.7-alpine

WORKDIR /app
COPY . /app

RUN apk add --no-cache --update postgresql postgresql-dev gcc musl-dev
RUN pip install -r requirements.txt

CMD ["python", "app_local.py"]
