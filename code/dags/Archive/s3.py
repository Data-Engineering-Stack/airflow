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



def some_fn():
    global test
    test = "this is a global variable @amin!"





def recieve_fn():
    print(test)



with DAG(
    's3_task',
    start_date=datetime(2023, 9, 9),  
    schedule_interval='@daily', 
    default_args=default_args,
    catchup=False,  # Set to False if you don't want to backfill
    max_active_runs=1,
) as dag:


    @task()
    def s3_task():
        import boto3

        # Replace 'your_access_key_id' and 'your_secret_access_key' with your actual AWS credentials
        aws_access_key_id = 'test'
        aws_secret_access_key = 'test'
        region_name = 'us-east-1'  # e.g., 'us-east-1'
        bucket_name = 'sample-bucket'
        endpoint_url='http://localstack.localstack.svc.cluster.local'

        # Create an S3 client
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=region_name,
                        endpoint_url=endpoint_url)

        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)

        # Print the list of files
        for obj in response.get('Contents', []):
            print(f"File: {obj['Key']}")


    s3_task = s3_task()

s3_task









