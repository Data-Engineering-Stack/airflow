from __future__ import annotations
from datetime import datetime, timedelta
from textwrap import dedent
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import get_current_context
from airflow.models.param import Param
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor


postgres_conn_id='internal_postgres'

def check_previous_task_success(task_id=None,**kwargs):
    dag_id = kwargs['dag'].dag_id
    sql =f"""select state from public.task_instance where task_id ='{task_id}' and dag_id ='{dag_id}'
    and lower(state)!= 'running' and
    run_id != (select max(run_id) from public.task_instance where task_id ='{task_id}' and dag_id ='{dag_id}')
    and job_id is not null order by job_id desc limit 1"""

    db_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    res = db_hook.get_records(sql)

    for row in res:
        prev_task_state = row[0]

    if prev_task_state == 'success':
        return False # skip the downstream task if prev dag run task instance was successfull
    return True  



with DAG(
    "tutorial0",
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'trigger_rule': 'all_success'
    },
    # [END default_args]
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    # [END instantiate_dag]

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    # [START basic_task]
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
        depends_on_past=True
    )
# Define your task
    def my_task():
        # Your task logic goes here
        print("Task executed.")

    # Create a ShortCircuitOperator to check the previous run's status
    check_previous_task = ShortCircuitOperator(
        task_id='check_previous_task',
        python_callable=check_previous_task_success,
        op_args=['print_date'],
        provide_context=True,
        dag=dag,
    )

    task2 = PythonOperator(
        task_id='my_task2',
        python_callable=check_previous_task_success,
        dag=dag,
    )

    # Define your task (replace with your actual task)
    task = PythonOperator(
        task_id='my_task',
        python_callable=my_task,
        dag=dag,
    )

    # Define the execution order
    t1 >> check_previous_task >> task2>> task
   

 
