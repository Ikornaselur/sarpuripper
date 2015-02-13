FROM python:2.7 
MAINTAINER Axel Örn Sigurðsson <axel@absalon.is>

ADD . /opt/streamcatcher
WORKDIR /opt/streamcatcher
EXPOSE 5000

RUN apt-get update
RUN apt-get install -y rtmpdump libav-tools

RUN pip install -r requirements.txt

ENTRYPOINT python src/worker.py
