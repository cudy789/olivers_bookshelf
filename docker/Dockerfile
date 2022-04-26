FROM ubuntu:20.04

RUN apt update && apt install python3 python3-pip

RUN pip3 install flask

COPY .. /app

CMD python3 /app/app.py
