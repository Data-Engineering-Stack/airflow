# import time
# from datetime import datetime, timedelta

# from airflow.decorators import dag, task

# """Example DAG demonstrating SLA use in Tasks"""


# # [START howto_task_sla]
# def sla_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
#     print(
#         "The callback arguments are: ",
#         {
#             "dag": dag,
#             "task_list": task_list,
#             "blocking_task_list": blocking_task_list,
#             "slas": slas,
#             "blocking_tis": blocking_tis,
#         },
#     )


# @dag(
#     schedule_interval="*/2 * * * *",
#     start_date=datetime(2021, 1, 1),
#     catchup=False,
#     sla_miss_callback=sla_callback,
#     default_args={'email': "email@example.com"},
# )
# def example_sla_dag():
#     @task(sla=timedelta(seconds=10))
#     def sleep_20():
#         """Sleep for 20 seconds"""
#         time.sleep(20)

#     @task
#     def sleep_30():
#         """Sleep for 30 seconds"""
#         time.sleep(30)

#     sleep_20() >> sleep_30()


# dag = example_sla_dag()

# # [END howto_task_sla]