# From https://towardsdatascience.com/how-to-run-jupyter-notebook-on-docker-7c9748ed209f
ARG BASE_CONTAINER=jupyter/pyspark-notebook
FROM $BASE_CONTAINER
LABEL author="Kevin George"
USER root
RUN pip install findspark confluent_kafka pyspark flask nltk 


FROM confluentinc/cp-kafka-connect:7.3.0
COPY --from=builder /kafka-questdb-connector/*.jar /usr/share/java/kafka/

FROM alpine:latest AS builder
RUN wget https://github.com/questdb/kafka-questdb-connector/releases/download/v0.4/kafka-questdb-connector-0.4-bin.zip && \
    unzip kafka-questdb-connector-*-bin.zip
    

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

ENV JUPYTER_ENABLE_LAB="yes"

RUN ls
COPY --chown=jovyan:users app.py /home/jovyan/work
COPY --chown=jovyan:users ./spark_demo.ipynb /home/jovyan/work
COPY --chown=jovyan:users ./cryptofeed_producers.py /home/jovyan/work
COPY ./jars/spark-sql-kafka-0-10_2.12-3.0.0.jar /opt/conda/lib/python3.8/site-packages/pyspark/jars
