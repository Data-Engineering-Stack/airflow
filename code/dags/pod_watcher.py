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
from airflow.operators.email_operator import EmailOperator
from airflow.models import Variable

postgres_conn_id='internal_postgres'

init = {
    'notification_emails' : str(Variable.get("notification_emails"))
}

def callback_f(context):
    subject = "Monitor/Prod: Pod Failed! "
    html = context["task_instance"].xcom_pull(task_ids="monitor_pods")
    send_email = EmailOperator(
        task_id='send_email_task',
        to=init['notification_emails'],  # Replace with the recipient's email address
        subject=subject,
        html_content=html,
    )

    send_email.execute(context=context)


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
    'on_failure_callback': callback_f, # or list of functions
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
    

    # monitor = BashOperator(
    #     task_id="monitor",
    #     bash_command=f"""python /opt/airflow/dags/repo/code/dags/watch_pods.py """,
    # )

    monitor_pods = PythonOperator(
        task_id="monitor_pods",
        python_callable=monitor_py,
        do_xcom_push=True
    )

#monitor
monitor_pods