#!/bin/bash
FROM node:alpine

WORKDIR /usr/src/app

RUN npm install redis
RUN npm install websocket
RUN npm install @questdb/nodejs-client

RUN apk add --no-cache bash

COPY . .

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

