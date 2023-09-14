from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime,timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python import get_current_context
from airflow.models import Variable
import io

memory_file = io.StringIO()
postgres_conn_id='internal_postgres'

init = {
    'notification_emails' : str(Variable.get("notification_emails"))
}

default_args={
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



def get_previous_run_task_status(dag_id, task_id):
    from airflow.models import DagRun, TaskInstance
    # Find the previous DagRun
    prev_dag_run = DagRun.find(
        dag_id=dag_id,
        state="success",
        execution_date=DagRun.get_previous_dagrun(dag_id).execution_date,
        include_subdags=False,
    )

    if prev_dag_run:
        # Find the TaskInstance for the specified task in the previous DagRun
        prev_task_instance = TaskInstance(
            task=task_id,
            execution_date=prev_dag_run.execution_date,
        )
        print(prev_task_instance)
        print(f"end_Date: {prev_task_instance.end_date}")
        # Get the status of the task in the previous DagRun
        task_status = prev_task_instance.current_state()
        print(f"task_Status_amin: {task_status}")
        return task_status
    else:
        return None

def print_previous_task_status(**kwargs):
    task_id = 'postgres_task'  # Replace with your actual task ID
    previous_task_status = get_previous_run_task_status(kwargs['dag'].dag_id, task_id)
    print(f"Previous Run Task Status for Task {task_id}: {previous_task_status}")


def send_email(subject,html):
    email_task = EmailOperator(
    task_id='send_email_task',
    to=init['notification_emails'],  # Replace with the recipient's email address
    subject=subject,
    html_content=html,  # HTML content with the DataFrame table
    )

    email_task.execute(get_current_context())

# Define the SQL query you want to execute
query1 = """
 select * from dag_run limit 1;
"""
query2 = """
 select * from task_instance limit 1;
"""

def my_task(query):
    from datetime import datetime
    now = datetime.today()
    db_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    df_html = db_hook.get_pandas_df(sql=query).to_html(index=False)
    html_body = "Please find the below result:<br><br>"
    html_end = "<br>Regards,<br>Airflow-bot :)<br>Have a great day!<br>"
    memory_file.write(html_body + df_html + html_end)
    send_email(f'Monitor/Prod: [dag statistics] - {now}',memory_file.getvalue())
    memory_file.close()
    return True


# Define your Airflow DAG

with DAG(
    'query_postgres_table',
    start_date=datetime(2023, 9, 9),  
    schedule_interval=None, 
    default_args=default_args,
    catchup=False  # Set to False if you don't want to backfill
) as dag:


    query1 = PythonOperator(
        task_id='postgres_task',
        python_callable=my_task,
        op_args = [query1]
    )

    task1 = PythonOperator(
        task_id='task1',
        python_callable=print_previous_task_status,
        provide_context=True,
        dag=dag,
    )

query1
task1

