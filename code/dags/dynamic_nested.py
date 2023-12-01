from airflow import DAG,Dataset
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime,timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python import get_current_context
from airflow.models import Variable
import io
from airflow.operators.bash import BashOperator
from airflow.sensors.bash import BashSensor
from airflow.operators.python import get_current_context
from airflow.decorators import dag, task
from airflow.utils.state import State

default_args={
    "depends_on_past": False,
    # "email": ["airflow@example.com"],
    # "email_on_failure": True,
    # "email_on_retry": False,
    # "retries": 1,
    # "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    #'sla': timedelta(seconds=5),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function, # or list of functions
    # 'on_success_callback': some_other_function, # or list of functions
    # 'on_retry_callback': another_function, # or list of functions
    # 'sla_miss_callback': yet_another_function, # or list of functions
    # 'trigger_rule': 'all_success'
}

configs = {
    "ho": {"schema": "P8206A", "dataset": "zh_ho"},
    "fz": {"schema": "P8207A", "dataset": "zh_fz"},
}

# create list for expand:
configs_lst = [[value["schema"], value["dataset"]] for key, value in configs.items()]


def test():
    print("==============ok")
    return "============ok"


with DAG(
    'dynamic_nested',
    start_date=datetime(2023, 9, 9),  
    schedule_interval='@daily', 
    default_args=default_args,
    catchup=False,  # Set to False if you don't want to backfill
    max_active_runs=1,
) as dag:




    @task(outlets=Dataset('test'))
    def task1(configs_lst=configs_lst):

        schema =configs_lst[0]
        dataset = configs_lst[1]
        print(f"schema: {schema} and dataset: {dataset}")

        task1 = BashOperator(
        task_id="task1",
        bash_command=f'echo {schema}',
        outlets=f"Dataset({dataset})",
        on_success_callback=test
    )
        
        task1.execute(context=get_current_context())
        
    

    task1 = task1.expand(configs_lst=configs_lst)


    @task
    def print_triggering_dataset_events(triggering_dataset_events=None):
        for dataset, dataset_list in triggering_dataset_events.items():
            print(dataset, dataset_list)
            print(dataset_list[0].source_dag_run.dag_id)

    print_triggering_dataset_events()








    task1





