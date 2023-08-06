from datetime import datetime
from airflow.models import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from deploy_k8s import get_executor_config

app = '/opt/airflow/dags/repo/code/dags/sparkcode.py'


with DAG('spark_job',schedule=None,start_date=datetime(2022, 3, 4),catchup=False) as dag:


    SparkSubmitOperator_task = SparkSubmitOperator(
    task_id='SparkSubmitOperator_task',
    application=app,
    conf=None,
    conn_id='spark_conn',
    verbose=False,
    name='testspark',
    executor_config=get_executor_config()
    )




SparkSubmitOperator_task