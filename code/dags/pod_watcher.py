from airflow import DAG,XComArg
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
    # "email": ["airflow@example.com"],,
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




def monitor_py():
    from watch_pods import monitor_specific_pod
    namespace = 'airflow'
    pod_name_prefix = "airflow-"
    monitor_specific_pod(namespace,pod_name_prefix)



with DAG(
    'pod_watcher',
    start_date=datetime(2023, 9, 9),  
    schedule_interval=None, 
    default_args=default_args,
    doc_md="Dag to monitor pod",
    catchup=False,  
    max_active_runs=1
) as dag:
    

    monitor = BashOperator(
        task_id="monitor",
        bash_command=f"""python /opt/airflow/dags/repo/code/dags/watch_pods.py """,
    )

    monitor_pods = PythonOperator(
        task_id="python_task",
        python_callable=monitor_py,
        do_xcom_push=True
    )

#monitor
monitor_pods