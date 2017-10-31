FROM python:alpine

ENV app /captcha-audio


RUN apk update
RUN apk add sox
RUN apk --no-cache add musl-dev linux-headers g++

RUN mkdir $app

COPY requirements.txt .
COPY *.py $app/
COPY captcha_data.db $app

RUN pip install -r requirements.txt

WORKDIR $app
