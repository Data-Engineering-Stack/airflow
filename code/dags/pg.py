from airflow import DAG
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


from airflow.operators.python import get_current_context

def get_prev_state(dag,task_id):
    print(dag)
    # context = get_current_context()
    # ti = context["ti"]
    # print(ti.dag_id)
    sql = f""" select TO_CHAR(prev_ti_end_date, 'YYYY-MM-DD HH24:MI:SS.MS') from (
    select 
    case when lower(state)='success' then end_date at TIME zone 'CEST' else Start_Date at time zone 'CEST' end as prev_ti_end_date
    from task_instance where task_id='{task_id}' and  dag_id='{dag.dag_id}' and state != 'running'
    and run_id != (select max(run_id) from task_instance where task_id='{task_id}'
    and  dag_id='{dag.dag_id}')     order by run_id desc limit 1 ) q1 """
    print(sql)
    db_hook = PostgresHook(postgres_conn_id=postgres_conn_id)

    res = db_hook.get_records(sql)

    for row in res:
        formatted_timestamp = row[0]
        print(formatted_timestamp)
    

    if formatted_timestamp is None:
        print('result is empty!!!!')

    return formatted_timestamp

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
    catchup=False,  # Set to False if you don't want to backfill
    user_defined_macros={"my_macro":get_prev_state}
) as dag:

    state = "'{{ my_macro(dag,'postgres_task') }}'"

    bash_task = BashSensor(
        task_id="bash_task",
        bash_command=f'find . type -f iname "x.*" -newermt "{state}" -mmin+1 | grep .',
        poke_interval=10,
        timeout = 60,
        mode= "poke"
        # env: Optional[Dict[str, str]] = None,
        # output_encoding: str = 'utf-8',
        # skip_exit_code: int = 99,
    )

    query1 = PythonOperator(
        task_id='postgres_task',
        python_callable=my_task,
        op_args = [query1]
    )

    # postgres_task = PythonOperator(
    #     task_id='get_prev_state',
    #     python_callable=get_prev_state,
    #     op_args = ['postgres_task']
    # )

query1
# postgres_task
bash_task



