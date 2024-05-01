import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import timedelta



def minutes_till_midnight():
    from datetime import datetime
    import pytz
    
    # Set the timezone to Europe/Berlin
    berlin_tz = pytz.timezone('Europe/Berlin')
    
    # Hardcode 5 PM CET time
    cet_5pm = berlin_tz.localize(datetime.now().replace(hour=21, minute=0, second=0, microsecond=0))

    # Calculate the difference in seconds between current time and 5 PM CET
    time_until_5_pm_cet = (cet_5pm - datetime.now(berlin_tz)).total_seconds()

    # Convert seconds to minutes and round off to the nearest minute
    minutes_until_5_pm_cet = round(time_until_5_pm_cet / 60)

    return minutes_until_5_pm_cet


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

