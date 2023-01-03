FROM python:3.9-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install --upgrade -r /code/requirements.txt

COPY ./app ./app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

