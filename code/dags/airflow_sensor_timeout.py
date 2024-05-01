import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import timedelta


def minutes_till_midnight():
    return 2

with DAG(
    dag_id="airflow_sensor_timeout",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule="@daily",
    dagrun_timeout = timedelta(minutes=minutes_till_midnight()),
    tags=["sensor"],
) as dag:
    
    BashOperator(
        task_id="producer_trigger_dataset",
        bash_command="sleep 5",
    )

