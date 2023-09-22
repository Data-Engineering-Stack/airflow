"""
TimeDeltaSensor
"""
from __future__ import annotations

import datetime

import pendulum

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.time_delta import TimeDeltaSensor
from datetime import timedelta

with DAG(
    dag_id="TimeDeltaSensorExample",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
) as dag:
    wait = TimeDeltaSensor(task_id="wait", 
                           delta=datetime.timedelta(seconds=30),
                           mode='poke',
                           poke_interval=60,
                           timeout=timedelta(minutes=5)
                           
                           )
    finish = EmptyOperator(task_id="finish")
    wait >> finish