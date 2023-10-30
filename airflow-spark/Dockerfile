# This Dockerfile contains a modified version of the airflow base image to support Apache spark local execution.
FROM apache/airflow:2.6.0-python3.8
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless bzip2\
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# install custom pip packages
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.0.0 \
    findspark==2.0.1 \
    pyspark==3.3.1 

# Download spark jars
COPY download_spark_packages.py /opt/airflow/download_spark_packages.py
COPY spark_dependencies.txt /opt/airflow/spark_dependencies.txt
RUN python /opt/airflow/download_spark_packages.py

# Download assembled jar for exasol connector
RUN curl -O -L --create-dirs https://github.com/exasol/spark-connector/releases/download/1.2.2/spark-connector_2.12-1.2.2-spark-3.2.2-assembly.jar --output-dir home/airflow/.ivy2/jars/







