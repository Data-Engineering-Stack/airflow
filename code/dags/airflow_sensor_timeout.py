import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import timedelta
from airflowKick import minutes_till_midnight



# def minutes_till_midnight():
#     from datetime import datetime
#     import pytz

#     berlin_tz = pytz.timezone('Europe/Berlin')
#     now = datetime.now(berlin_tz)
#     end_of_day = berlin_tz.localize(datetime(now.year, now.month, now.day, 23, 59, 59))
#     remaining_time = end_of_day - now
#     return remaining_time.seconds // 60


with DAG(
    dag_id="airflow_sensor_timeout",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule="@daily",
    dagrun_timeout = timedelta(minutes=minutes_till_midnight()),
    tags=["sensor"],
) as dag:
    
    BashOperator(
        task_id="producer_trigger_dataset",
        bash_command="sleep 3000",
    )

