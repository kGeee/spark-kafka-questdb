#!/bin/bash
FROM --platform=linux/amd64 python:3.9-slim-buster as build
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

COPY ./fastapp.py /code/fastapp.py
COPY ./__init__.py /code/__init__.py
COPY ./queries.json /code/queries.json
ADD perspective_src /code/perspective_src
ADD static /code/static

# 
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt
RUN python3 -m pip install requests
RUN python3 -m pip install perspective-python
# 


ENV WEBSERVER_PORT=64013

EXPOSE 64013

# 
CMD ["python3", "fastapp.py"]
