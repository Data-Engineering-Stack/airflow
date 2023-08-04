"""Example DAG demonstrating the usage of dynamic task mapping."""
from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import  PythonOperator

def dum(x):
    print(f"hi, the number is {x}")


with DAG(dag_id="example_dynamic_task_mapping", start_date=datetime(2022, 3, 4),catchup=False) as dag:

    # @task
    # def add_one(x: int):
    #     return x + 1

    # @task
    # def sum_it(values):
    #     total = sum(values)
    #     print(f"Total was {total}")

    # added_values = add_one.expand(x=[1, 2, 3])
    # sum_it(added_values)

    
    python_test = PythonOperator.partial(
            task_id="python_test_task",
            python_callable=dum,
        ).expand(op_kwargs=[{'x':'1'}, {'x':'2'}, {'x':'3'}])
##.expand(op_kwargs=XComArg(some_previous_task, key='return_value'))
python_test