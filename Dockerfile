FROM apache/airflow:2.6.3-python3.10

USER root
COPY ./r.txt /opt/airflow

USER airflow
RUN --mount=type=cache,target=/root/.cache/pip pip install -r r.txt



