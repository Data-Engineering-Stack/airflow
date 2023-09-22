"""
TimeDeltaSensor
"""
from __future__ import annotations

import datetime

import pendulum

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.time_delta import TimeDeltaSensor
from datetime import timedelta,datetime
from airflow.operators.python import PythonOperator

def printer():
    print(datetime.now())
    return True

with DAG(
    dag_id="TimeDeltaSensorExample",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
) as dag:
    wait = TimeDeltaSensor(
        task_id="wait", 
        delta=timedelta(seconds=30),
        mode='poke',
        poke_interval=60,
        timeout=timedelta(minutes=5)
        )

    execute_task = PythonOperator(
        task_id='execute_task',
        python_callable=printer,
        provide_context=True,
        dag=dag
    )


    wait >> execute_task