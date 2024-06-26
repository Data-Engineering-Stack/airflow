from datetime import datetime
from airflow.models import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from deploy_k8s import get_executor_config,get_spark_config

app = '/opt/airflow/dags/repo/code/dags/sparkcode.py'


spark_configurations = {
    "spark.driver.port": "42000",  # The name of your Spark application.
    "spark.driver.blockManager.port": "42016",  # The name of your Spark application.
    "spark.blockManager.port": "42032",  # The name of your Spark application.
    "spark.executor.memory": "1g",  # Memory allocated per executor.
    "spark.driver.memory": "1g",  # Memory allocated for the driver.
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",  # Serializer for data.
    "spark.dynamicAllocation.enabled":"false",
    # "spark.driver.host" : "{{ task_instance.hostname }} "
}

#"{{ task_instance.hostname }}.spark-headless-service.airflow.svc.cluster.local "


with DAG('spark_job',schedule=None,start_date=datetime(2022, 3, 4),catchup=False) as dag:


    SparkSubmitOperator_task = SparkSubmitOperator(
    task_id='SparkSubmitOperator_task',
    application=app,
    conf=get_spark_config(),
    conn_id='spark_conn',
    verbose=True,
    name='testspark',
    executor_config=get_executor_config()
    )




SparkSubmitOperator_task