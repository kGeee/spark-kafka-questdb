#!/bin/bash
FROM --platform=linux/amd64 alpine:latest AS builder

RUN wget https://github.com/questdb/kafka-questdb-connector/releases/download/v0.4/kafka-questdb-connector-0.4-bin.zip && \
    unzip kafka-questdb-connector-*-bin.zip
    
FROM confluentinc/cp-kafka-connect:7.3.0
COPY --from=builder /kafka-questdb-connector/*.jar /usr/share/java/kafka/

ENV CONNECT_BOOTSTRAP_SERVERS=provider.bdl.computer:32397
ENV CONNECT_REST_ADVERTISED_HOST_NAME=connect
ENV CONNECT_REST_PORT=8083
ENV CONNECT_GROUP_ID=compose-connect-group
ENV CONNECT_CONFIG_STORAGE_TOPIC=docker-connect-configs
ENV CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR=1
ENV CONNECT_OFFSET_FLUSH_INTERVAL_MS=10000
ENV CONNECT_OFFSET_STORAGE_TOPIC=docker-connect-offsets
ENV CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR=1
ENV CONNECT_STATUS_STORAGE_TOPIC=docker-connect-status
ENV CONNECT_STATUS_STORAGE_REPLICATION_FACTOR=1
ENV CONNECT_KEY_CONVERTER=org.apache.kafka.connect.storage.StringConverter
ENV CONNECT_VALUE_CONVERTER=org.apache.kafka.connect.json.JsonConverter