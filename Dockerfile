FROM apache/airflow:2.7.0-python3.10

USER root
COPY ./r.txt /opt/airflow
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bzip2\
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean;

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow
RUN --mount=type=cache,target=/root/.cache/pip pip install -r r.txt

RUN pip install --no-cache-dir \
    dbt-postgres==1.5.0 \
    apache-airflow-providers-apache-spark==4.1.0 \
    apache-airflow-providers-postgres==5.5.0 \
    findspark==2.0.1 \
    pyspark==3.2.1 \
    pynessie==0.48.2 



