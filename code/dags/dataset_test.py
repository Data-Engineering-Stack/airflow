import pendulum
import random
from airflow import DAG, Dataset
from airflow.operators.bash import BashOperator

from datetime import timedelta
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.context import Context
from airflow.utils.session import NEW_SESSION, provide_session
from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import Union,Any
from dateutil import parser


import pytz
from airflow.utils.db import provide_session
from airflow.models.dataset import DatasetDagRunQueue, DatasetEvent, DatasetModel
from datetime import datetime
from airflow.utils.session import create_session

from airflow.providers.postgres.hooks.postgres import PostgresHook

postgres_conn_id='internal-postgres'

class DatasetSensor(BaseSensorOperator):
    """
    Waits for a dataset being produced for the given consumer dag execution_date and return dataset URI as XCOM
    
    :param execution_date: Execution date for which to check the dataset's status as ISO-formatted string or datetime (templated)
    
    :usage:
    DatasetSensor(
        task_id="DataSensorTask",
        execution_date="{{data_interval_start}}",
        poke_interval=60 * 1,
        mode="reschedule",  
        timeout=60 * 10, 
    )
    """

    template_fields = ["execution_date"]

    def __init__(
        self,
        *,
        execution_date: Union[str, datetime],
        **kwargs,
    ):
        super().__init__(**kwargs)

        if isinstance(execution_date, datetime):
            self.execution_date = execution_date.isoformat()
        elif isinstance(execution_date, str):
            self.execution_date = execution_date
        else:
            raise TypeError(
                f"execution_date should be passed either as a str or datetime, not {type(execution_date)}"
            )

    #@provide_session
    def poke(self, context: Context, session: Session = NEW_SESSION) -> bool:
        """
        This function is used to poke a list of consumer dag's dataset and verify if
        dataset's date matches with the consumer dag execution date.

        Args:
            - self: Reference to the current object.
            - context (Context): Airflow context containing information about the task instance.
            - session (Session, optional): SQLAlchemy session. Defaults to NEW_SESSION.

        Returns:
            bool: True if the dataset is found, False otherwise.
        """
        
        db_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        dag_id = context['dag'].dag_id
        consumer_dag_start_ts = context["dag_run"].start_date
        cest = pytz.timezone("Europe/Berlin")
        triggering_dataset_events = context["triggering_dataset_events"]

        consumer_dag_start_date = parser.parse(self.execution_date).astimezone(cest).strftime("%Y-%m-%d %H:%M:%S %Z")
        print(f"consumer_dag_start_date: {consumer_dag_start_date}")
        consumer_dag_start =consumer_dag_start_ts.astimezone(cest).strftime("%Y-%m-%d %H:%M:%S")

        
        total_datasets = len(triggering_dataset_events)
        old_dataset_update = []
        new_dataset_update = []

        with create_session() as session: 
            for dataset, dataset_list in triggering_dataset_events.items():

                print(dataset, dataset_list)
                print(dataset_list[0].source_dag_run.dag_id)
                producer_dag_ts=dataset_list[0].source_dag_run.execution_date
                print(f"producer_dag_ts: {dataset_list[0].source_dag_run.execution_date}")
                print(f"consumer_dag_start_ts: {consumer_dag_start_ts}")
                
                last_update_dataset_ts = session.query(func.max(DatasetEvent.timestamp))\
                        .filter_by(dataset_id=dataset_list[0].dataset_id)\
                        .scalar()

                print(f"last_update_dataset_ts: {last_update_dataset_ts}")


                # catch old dataset update:
                if not (producer_dag_ts <= last_update_dataset_ts <= consumer_dag_start_ts):
                    # this case can only arise when consumer dag has started, when queue some datasets are in queue
                    # and are refreshed after that
                    # which means there were some old dataset which triggered this consumer dag
                    # we can wait until this condiditon becomes true for old dataset as well!
                    new_dataset_update.append(dataset_list[0].source_dag_run.dag_id)
                    if dataset_list[0].source_dag_run.dag_id in old_dataset_update:
                        print('Old Dataset has been refreshed. Hence removing...')
                        old_dataset_update.remove(dataset_list[0].source_dag_run.dag_id)
                    print("We found a stale dataset!")

                    print(f"Removing  dataset id:  {dataset_list[0].dataset_id} from Queue...")
                    session.query(DatasetDagRunQueue).filter(
                                DatasetDagRunQueue.dataset_id == dataset_list[0].dataset_id
                            ).delete()

                else:

                    old_dataset_update.append(dataset_list[0].source_dag_run.dag_id)
                    print("Dataset is upto date!")
        

        if len(new_dataset_update) > 0 :
            required = total_datasets - len(new_dataset_update)
            self.log.info(
            "we have old datasets: %s. Poking untill all %s are refreshed...",
            old_dataset_update,
            required
        )

        if len(old_dataset_update) == 0 or len(old_dataset_update) == total_datasets:
            self.log.info(
                "Found all dataset produced on execution_date %s",
                self.execution_date,
            )
            
            context['ti'].xcom_push(key='dataset_uri', value=list(triggering_dataset_events.keys()))
            #clear up the queue as well!
            # print(f"Clearing up the Queue with dataset id : {dataset_list[0].dataset_id} ...")
            # delete_sql=f"delete from public.dataset_dag_run_queue where dataset_id = '{dataset_list[0].dataset_id}'"
            # res_del = db_hook.get_first(delete_sql)
            # print(f"deleted rec cnt: {res_del}")


            
            return True


        return False





                
        ## information:
        ##############
        #1. Only when an outlet dataset on a task completes successfully, a DatasetDagRunQueue is logged.
        ## Caveats:
        ############
        # 1. Once the consumer dag start, it clears up the Queue!
        # 2. But we can still get dataset created_at value i suppose
        
        # counter = 0
        # print(f'check that no dagruns were queued...{session.query(DatasetDagRunQueue).count()}')
        # #assert session.query(DatasetDagRunQueue).count() == 0

        # print(f' count of Queue: {session.query(DatasetDagRunQueue).filter_by(target_dag_id=dag_id).count()}')
        # if session.query(DatasetDagRunQueue).filter_by(target_dag_id=dag_id).count() > 0:
        #     for uri, dataset in triggering_dataset_events.items():
        #         print(uri,dataset)
                
        #         ddrq_created_at = (
        #                         session.query(DatasetDagRunQueue.created_at).filter_by(dataset_id=dataset[0].dataset_id).all()
        #                 )

        #         print(f"{uri} created at : {ddrq_created_at} , {type(ddrq_created_at)}")
                
                
                
        #         ddrq = (
        #                         session.query(DatasetDagRunQueue).filter_by(dataset_id=dataset[0].dataset_id).all()
        #                 )
                
                
        #         print(f"{uri} info : {ddrq} , {type(ddrq)}")
                
        #         if  ddrq_created_at > consumer_dag_start:
        #             counter+=1
                
            

            
            
        # STORE THE VALUES:
        # sql=f"""  select distinct producer_dag,dataset_uri
        #             from public.dataset_dependency_validator where parent_producer_dag='{dag_id}'
        #             and "CHECK_DATASET_VALIDITIY"=FALSE """
        # res = db_hook.get_pandas_df(sql)
        # print(f"waiting for updated dataset : {res.to_markdown(index=False)}")
        
        
        # check whether anything in queue for this dag
        #debug_sql = f"select * from public.dataset_dag_run_queue where target_dag_id = '{dag_id}'"
        # debug_sql = f"""select distinct dataset_id from
        # public.dataset_dependency_validator where consumer_dag = '{dag_id}'
        # and last_dataset_update_ts < '{consumer_dag_start}'
        # and dataset_queue_created is null
        # """

            
            
        # print(debug_sql)
    
        # debug_sql=db_hook.get_pandas_df(debug_sql)
        # print(f"Dataset in queue: {debug_sql.to_markdown(index=False)}")

        # # capture the dataset_id from above
        # distinct_dataset_id = debug_sql['dataset_id'].unique().tolist()
        # print(f'queued dataset id: {distinct_dataset_id}')
        
        # triggered_by_dataset = [dataset_list[0].dataset_id for  _, dataset_list in triggering_dataset_events.items()]
        # print(f'triggered_by_dataset: {triggered_by_dataset}')
        # counter = 0

        # #old_dataset = list(set(distinct_dataset_id) - set(triggered_by_dataset))
        # if len(distinct_dataset_id) > 1: #only considering mutliple datasets
        #     #datasets_difference = list(set(triggered_by_dataset) ^ set(distinct_dataset_id))
        #     old_dataset = list(set(triggered_by_dataset) & set(distinct_dataset_id))
        #     print(f'common dataset : {old_dataset}')
            
        #     # if len(datasets_difference) == 0 :
        #     #     old_dataset = []
                
            
        #     # go to view, and POLL whether last_dataset_update_ts > dataset_queue_created
        #     for id in old_dataset:
        #         poll_sql = f"""
        #         select count(*) from
        #             public.dataset_dag_run_queue where target_dag_id = '{dag_id}'
        #             and created_at at time zone 'CET' > '{consumer_dag_start}'
        #         """
        #         check_count = db_hook.get_first(poll_sql)[0]
                
        #         print(f'checking if dataset with dataset id {id} got updated: {check_count}')
        #         if check_count > 0:
        #             print(f'SUCCESS: Dataset with dataset id {id} got updated: {check_count}')
        #             counter+=1
        #         # else:
        #         #     print("nothing in queue")
                
        # elif  len(distinct_dataset_id)==0:
        #     old_dataset = []
            
            
        # else:
        #     old_dataset = []




Producer_dataset = Dataset("/tmp/dagParent")


################## Producer:
with DAG(
    dag_id="dataset_producer",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule='@daily',
    tags=["debug","testing","dataset"],
) as dag0:
    
    BashOperator(outlets=[Producer_dataset], 
                task_id="producer_trigger_dataset", 
                bash_command="sleep 5")
    
################# ConsumerLevel1:

for i in range(1,5):
    with DAG(
    dag_id=f"dataset_consumer_level1_{i}",
    catchup=False,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=[Producer_dataset],
    tags=["debug","dataset","consumer","level1"],
    ) as dag:
        
        outlet = Dataset(f'level_2_{i}')

        if i == 2:
            task = BashOperator(outlets=[outlet], 
                task_id=f"consumer_level1_task_{i}", 
                bash_command="exit $((RANDOM % 2))")
            
        # elif i ==8:
        #     task = BashOperator(outlets=[outlet], 
        #             task_id=f"consumer_level1_task_{i}", 
        #             bash_command="sleep 15")
        
            
        else:
            task = BashOperator(outlets=[outlet], 
                    task_id=f"consumer_level1_task_{i}", 
                    bash_command="sleep 5")
        
        ValidateDataset = DatasetSensor(
            task_id=f"ValidateDataset{i}",
            execution_date="{{data_interval_start}}",
            poke_interval=5 * 1,
            mode="reschedule",  
            timeout=60 * 10, 
        )
        
        ValidateDataset >> task

    

################# ConsumerLevel2:
dependency = [Dataset(f'level_2_{i}') for i in range(1, 5)]

with DAG(
    dag_id="dataset_consumer_level2",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=dependency,
    tags=["debug","testing","dataset","consumer","level2"],
) as dag:
    
    task = BashOperator( task_id="consumer_level2_task", 
                bash_command="sleep 5")
    
    ValidateDataset = DatasetSensor(
        task_id="ValidateDataset2",
        execution_date="{{data_interval_start}}",
        poke_interval=60 * 1,
        mode="reschedule",  
        timeout=60 * 10, 
    )
    
    ValidateDataset >> task   