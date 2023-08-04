FROM apache/airflow:2.6.3-python3.10

USER root
COPY ./r.txt /opt/airflow
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bzip2\
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN --mount=type=cache,target=/root/.cache/pip pip install -r r.txt

RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.0.0 \
    findspark==2.0.1 \
    pyspark==3.2.1 \
    pynessie==0.48.2 



