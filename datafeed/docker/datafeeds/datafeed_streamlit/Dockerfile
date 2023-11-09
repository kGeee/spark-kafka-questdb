#!/bin/bash
FROM node:alpine

WORKDIR /usr/src/app

RUN apk add --no-cache python3 py3-pip make g++

RUN pip install pandas streamlit 


COPY . .

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

