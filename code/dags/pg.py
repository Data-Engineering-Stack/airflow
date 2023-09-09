from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python import get_current_context

postgres_conn_id='internal_postgres'


# Define the SQL query you want to execute
sql_query = """
 select * from dag_run;
"""

def my_task():
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    df = hook.get_pandas_df(sql=sql_query)
    df_html = df.to_html(index=False)

    html_content = f""" Please find the below dags:\n\n{df_html}"""
    email_task = EmailOperator(
    task_id='send_email_task',
    to='aminsiddique95@gmail.com',  # Replace with the recipient's email address
    subject='DataFrame Table in Email',
    html_content=html_content,  # HTML content with the DataFrame table
    )

    email_task.execute(get_current_context())

    return df_html



# Define your Airflow DAG

with DAG(
    'query_postgres_table',
    start_date=datetime(2023, 9, 9),  # Adjust the start date accordingly
    schedule_interval=None,  # Set your desired schedule interval or None for manual execution
    catchup=False  # Set to False if you don't want to backfill
) as dag:


# Create a PostgresOperator to execute the query
    # query_task = PostgresOperator(
    #     task_id='query_postgres_task',
    #     postgres_conn_id=postgres_conn_id,  # Specify your Postgres connection ID
    #     sql=sql_query,
    #     dag=dag
    # )
    run_this = PythonOperator(
        task_id='postgres_task',
        python_callable=my_task,
    )




run_this

