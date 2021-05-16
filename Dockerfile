FROM python:3.9.2-slim-buster

LABEL maintainer="Jesse Egbosionu <j3bsie@gmail.com>"
WORKDIR /trdbot

RUN apt-get update && apt-get install -y netcat supervisor 

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn", "main:app", "-b 0.0.0.0:5000", "--workers=2"]
