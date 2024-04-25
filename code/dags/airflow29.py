import pendulum
import random
from airflow import DAG, Dataset
from airflow.operators.bash import BashOperator
from airflow.timetables.datasets import DatasetOrTimeSchedule
from airflow.timetables.trigger import CronTriggerTimetable


Producer_dataset_1 = Dataset("Producer_dataset_1")
Producer_dataset_2 = Dataset("Producer_dataset_2")




################## Producer:
with DAG(
    dag_id="daily_runner_1",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule='@daily',
    tags=["debug","testing","dataset"],
) as dag0:
    
    BashOperator(outlets=[Producer_dataset_1], 
                task_id="producer_trigger_dataset", 
                bash_command="sleep 5")
    
with DAG(
    dag_id="daily_runner_2",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule='@monthly',
    tags=["debug","testing","dataset"],
) as dag0:
    
    BashOperator(outlets=[Producer_dataset_2], 
                task_id="producer_trigger_dataset", 
                bash_command="sleep 5")
    

with DAG(
    dag_id="Consumer_1",
    catchup=False,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=DatasetOrTimeSchedule(
        timetable=CronTriggerTimetable("40 20 * * *", timezone="UTC"),
        datasets=[Producer_dataset_1,Producer_dataset_2 ],
    ),
    tags=["debug","dataset","consumer","level1"],
    ) as dag:
        
        task = BashOperator(
            task_id="consumer_task", 
            bash_command="exit $((RANDOM % 2))")
        