FROM bitnami/spark:3.0.0

USER root
RUN apt-get update && apt-get install -y curl

USER 1001
RUN pip3 install --upgrade pip && pip3 install wheel

RUN pip install --no-cache-dir \
    findspark==2.0.1 \
    pyspark==3.2.1 

RUN rm -r /opt/bitnami/spark/jars && \
    curl --location http://mirror.cc.columbia.edu/pub/software/apache/spark/spark-3.0.0/spark-3.0.0-bin-hadoop2.7.tgz | \
    tar --extract --gzip --strip=1 --directory /opt/bitnami/spark/ spark-3.0.0-bin-hadoop2.7/jars/