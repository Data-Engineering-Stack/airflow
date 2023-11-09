# from __future__ import annotations

# import pendulum

# from airflow import DAG, Dataset
# from airflow.operators.bash import BashOperator

# # [START dataset_def]
# dag1_dataset = Dataset("/tmp/dag1/output_1.txt", extra={"hi": "bye"})

# # [END dataset_def]
# dag2_dataset = Dataset("/tmp/dag2/output_1.txt", extra={"hi": "bye"})


# with DAG(
#     dag_id="dataset_producer1",
#     catchup=False,
#     start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
#     schedule="@daily",
#     tags=["produces", "dataset-scheduled"],
# ) as dag1:
#     # [START task_outlet]
#     BashOperator(outlets=[dag1_dataset], task_id="producing_task_1", bash_command="sleep 5")
#     # [END task_outlet]

# with DAG(
#     dag_id="dataset_producer2",
#     catchup=False,
#     start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
#     schedule="@daily",
#     tags=["produces", "dataset-scheduled"],
# ) as dag1:
#     # [START task_outlet]
#     BashOperator(outlets=[dag2_dataset], task_id="producing_task_1", bash_command="sleep 5")
#     # [END task_outlet]



# with DAG(
#     dag_id="dataset_consumer",
#     catchup=False,
#     start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
#     schedule=[dag1_dataset, dag2_dataset],
#     tags=["consumer"],
# ) as dag2:
#     BashOperator( task_id="consumer_task_2", bash_command="sleep 5")