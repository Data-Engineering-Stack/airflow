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
from airflow.datasets.manager import dataset_manager
from airflow.utils.session import NEW_SESSION, provide_session
from sqlalchemy.orm.session import Session
from airflow.models.dataset import DatasetDagRunQueue, DatasetEvent, DatasetModel

from airflow.listeners.listener import get_listener_manager

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
    "ho": {"schema": "P8206A", "dataset": Dataset("ds_1")},
    "fz": {"schema": "P8207A", "dataset": Dataset("ds_2")},
}

# create list for expand:
configs_lst = [[value["schema"], value["dataset"]] for key, value in configs.items()]


def test(**context):
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

    # task0 = BashOperator(
    # task_id="task0",
    # bash_command=f'sleep 1',
    # outlets=[Dataset("zh_ho")]
    # )

    # @provide_session
    # @task.python(task_id="generate_dataset", on_failure_callback=lambda x: None)
    # def executable_func(session: Session = NEW_SESSION, **context: TaskInstance) -> list[Dataset]:
    #     datasets = [Dataset(f"s3://potato-{random.randint(1, 4)}"), Dataset("s3://tomato")]
    #     for dataset in datasets:
    #         stored_dataset = session.query(DatasetModel).filter(DatasetModel.uri == dataset.uri).first()
    #         if not stored_dataset:
    #             print(f"Dataset {dataset} not stored, proceeding to storing it")
    #             dataset_model = DatasetModel.from_public(dataset)
    #             session.add(dataset_model)
    #         else:
    #             print(f"Dataset {dataset} already stored, register dataset event instead")
    #             dm = DatasetManager()
    #             dm.register_dataset_change(task_instance=context["ti"], dataset=dataset, session=session)

    #     session.flush()
    #     session.commit()
    #     return datasets




    @provide_session
    @task.python()
    def task1(configs_lst=configs_lst, session=NEW_SESSION):
        context=get_current_context()
        ti = context["ti"]
        schema =configs_lst[0]
        dataset = configs_lst[1]


        print(f"schema: {schema} and dataset: {dataset}")

        task1 = BashOperator(
        task_id="task1",
        bash_command=f'echo {schema}'
        )
        

        task1.execute(context=context)

        stored_dataset = session.query(DatasetModel).filter(DatasetModel.uri == dataset.uri).first()

        if not stored_dataset:
            print(f"Dataset {dataset} not stored, proceeding to storing it")
            dataset_model = DatasetModel.from_public(dataset)
            session.add(dataset_model)
        else:
            print(f"Dataset {dataset} already stored, register dataset event instead")
            dataset_manager.register_dataset_change(task_instance=ti,dataset=dataset, session=session)
        

    task1 = task1.expand(configs_lst=configs_lst)


    @task
    def print_triggering_dataset_events(triggering_dataset_events=None):
        for dataset, dataset_list in triggering_dataset_events.items():
            print(dataset, dataset_list)
            print(dataset_list[0].source_dag_run.dag_id)

    print_triggering_dataset_events()








    task1





