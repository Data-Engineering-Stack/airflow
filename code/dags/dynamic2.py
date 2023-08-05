"""Example DAG demonstrating the usage of dynamic task mapping."""
from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import  PythonOperator
from airflow.decorators import task
from airflow.operators.python import get_current_context
from airflow.models.param import Param

tableschema= 'ABCD'
filename = "{{ params.filename }}"
tablename = "{{ params.target_table }}"


init = {
    'env': 'dev',
    'notification_emails' : 'airflow@airflow.net',
    's3_conn_id' : 's3_conn'

}

def ops(init,file_name,tablename,tableschema):
    print(f"{init}, the filename is {file_name} and tablename is {tableschema}.{tablename}")


with DAG(dag_id="test_expand", 
         start_date=datetime(2022, 3, 4),
         schedule_interval=None,
         params={
             'filename': Param("",type='string'),
             'target_table': Param("",type='string')
         },
         catchup=False
) as dag:

    @task
    def generate_args(init,tableschema):
        context = get_current_context()
        print(f'printing the context: {context}')
        config = context['dag_run'].conf
        list_kwargs = []

        op_kwargs={}
        op_kwargs['init'] = init
        op_kwargs['file_name'] = config['filename']
        op_kwargs['tablename'] = config['target_table']
        op_kwargs['tableschema'] = tableschema
        list_kwargs.append(op_kwargs)
        print(list_kwargs)
        return list_kwargs

    op_kwargs = generate_args(init,tableschema)


    python_test = PythonOperator.partial(
            task_id="python_test_task",
            python_callable=ops,
            do_xcom_push=False
        ).expand(op_kwargs=op_kwargs)

op_kwargs >> python_test