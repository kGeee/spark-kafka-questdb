#!/bin/bash
FROM --platform=linux/amd64 python:3.9-slim-buster as build
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./fastapp.py /code/fastapp.py
COPY ./dashapp.py /code/dashapp.py
COPY ./__init__.py /code/__init__.py

ADD producers /code/producers/

# 
CMD ["python3", "fastapp.py"]
