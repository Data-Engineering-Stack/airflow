FROM bitnami/spark:3.0.0

USER root
RUN apt-get update && apt-get install -y curl

RUN pip3 install --upgrade pip && pip3 install wheel

RUN pip install --no-cache-dir \
    findspark==2.0.1 \
    pyspark==3.2.1 

RUN rm -r /opt/bitnami/spark/jars && \
    curl --location https://dlcdn.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz | \
    tar --extract --gzip --strip=1 --directory /opt/bitnami/spark/ spark-3.5.0-bin-hadoop3/jars/


USER 1001