# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /frequentlymost

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

WORKDIR /frequentlymost/code/

CMD [ "python3", "./AzlyricsAPI.py" ]