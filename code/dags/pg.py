from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime,timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python import get_current_context
import io

memory_file = io.StringIO()
postgres_conn_id='internal_postgres'

init = {
    'notification_emails' : 'aminsiddique95@gmail.com'
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
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    df = hook.get_pandas_df(sql=query)
    df_html = df.to_html(index=False)
    html_body = "Please find the below dags:\n\n"
    memory_file.write(html_body)
    memory_file.write(df_html)
    memory_file_contents = memory_file.getvalue()
    send_email(f'Monitor/Prod: [dag statistics] - {now}',memory_file_contents)
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


query1

