from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta 
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import get_current_context
from airflow.models.param import Param
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

postgres_conn_id='internal_postgres'


default_args={
    "owner": "Amin",
    "depends_on_past": False,
    # "email": ["airflow@example.com"],
    # "email_on_failure": True,
    # "email_on_retry": False,
    # "retries": 1,
    # "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
     'priority_weight': 10,
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

dag_list_id = "{{ params.dag_id_list }}"



# 
def get_all_dags(dag):
    ''' returns list of all dags'''
    dag_list = []
    sql = f""" select dag_id from dag where dag_id != '{dag.dag_id}' limit 5 ; """
    db_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    res = db_hook.get_records(sql)

    for row in res:
        dag_id = row[0]
        print(dag_id)
        dag_list.append(dag_id)

    return dag_list


def verify_inputs(**kwargs):
    config = kwargs["dag_run"].conf

    if not bool(config):
        print("ok")


with DAG(
    'dag_inspector',
    start_date=datetime(2023, 9, 9),  
    schedule_interval=None, 
    default_args=default_args,
    doc_md="Dag to trigger n number of dags simultanelously",
    catchup=False,  
    max_active_runs=1,
    params={
        "dag_id_list" : Param("",type=["null", "string"],description="provide list of dag_ids in list to trigger")
    }
) as dag:
    
    verify_inputs = PythonOperator(
        task_id="python_task",
        python_callable=verify_inputs,
        # op_kwargs: Optional[Dict] = None,
        # op_args: Optional[List] = None,
        # templates_dict: Optional[Dict] = None
        # templates_exts: Optional[List] = None
    )



    # debug = BashOperator(
    #     task_id="debugger",
    #     bash_command=f"""echo "{dags}" """,
    # )

    @task(task_id="dag_triggerer")
    def dag_triggerer(dag_id):
        print(dag_id)
        trigger = TriggerDagRunOperator (
                task_id='start-ssh-job',
                trigger_dag_id=dag_id,
                wait_for_completion=False
                )
        trigger.execute(context=get_current_context())

    dag_triggerer = dag_triggerer.expand(dag_id=get_all_dags(dag))



    # @task(task_id="dag_triggerer")
    # def dag_triggerer(dag_id):
    #     trigger = BashOperator(
    #         task_id="dag_triggerer",
    #         bash_command=f"airflow dags trigger {dag_id}",
    #     )
    #     trigger.execute(context=get_current_context())

    # dag_triggerer = dag_triggerer.expand(dag_id=get_all_dags)




#debug 
verify_inputs >> dag_triggerer