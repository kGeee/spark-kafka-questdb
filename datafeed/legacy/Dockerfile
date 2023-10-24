# From https://towardsdatascience.com/how-to-run-jupyter-notebook-on-docker-7c9748ed209f
ARG BASE_CONTAINER=jupyter/pyspark-notebook
FROM $BASE_CONTAINER
LABEL author="Kevin George"
USER root
RUN pip install findspark confluent_kafka pyspark flask streamlit 

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

ENV JUPYTER_ENABLE_LAB="yes"

ADD --chown=jovyan:users ./src /home/jovyan/work/src
ADD --chown=jovyan:users ./producers /home/jovyan/work/producers
COPY --chown=jovyan:users ./jars/spark-sql-kafka-0-10_2.12-3.0.0.jar /opt/conda/lib/python3.8/site-packages/pyspark/jars
COPY --chown=jovyan:users ./jars/spark-sql-kafka-0-10_2.12-3.0.0.jar /home/jovyan/.ivy2/jars

RUN pip install -r /home/jovyan/work/src/requirements.txt

    
