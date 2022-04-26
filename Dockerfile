FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install python3 python3-pip -y

RUN pip3 install flask gspread oauth2client

COPY ./app.py /app/app.py
COPY ./templates /app/templates

WORKDIR /app

CMD python3 app.py