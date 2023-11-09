from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from lakefs_provider.operators.create_branch_operator import LakeFSCreateBranchOperator
from lakefs_provider.operators.commit_operator import LakeFSCommitOperator
from lakefs_provider.operators.merge_operator import LakeFSMergeOperator
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.models.dagrun import DagRun
import time
from functools import partial
from airflow.utils.log.logging_mixin import LoggingMixin

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    "owner": "lakeFS",
    "branch": "dev-airflow",
    "repo": "lakefs-repo",
    #"path": Variable.get("fileName"),
    "default-branch": "main",
    "lakefs_conn_id": 'lakefs-conn'
}

# The execution context and any results are automatically passed by task.post_execute method
def print_commit_result(context, result, message):
    LoggingMixin().log.info(message + result \
        + ' and lakeFS URL is: ' +"lakefsUIEndPoint" \
        + '/repositories/' + "main" + '/commits/' + result)

    
@dag(default_args=default_args,
     render_template_as_native_obj=True,
     max_active_runs=1,
     start_date=days_ago(2),
     schedule_interval=None,
     tags=['testing'])
def lakefs_wrapper_dag():
    # Create the branch to run on
    task_create_etl_branch = LakeFSCreateBranchOperator(
        task_id='create_etl_branch',
        branch=default_args.get('branch'),
        source_branch=default_args.get('default-branch')
    )
    
    task_create_etl_branch.post_execute = partial(print_commit_result, message='lakeFS commit id is: ')

    task_trigger = TriggerDagRunOperator(
        task_id="trigger_existing_dag",
        trigger_dag_id="lakefs_tutorial_taskflow_api_etl",  # Ensure this equals the dag_id of the DAG to trigger
        wait_for_completion="True",
        poke_interval=5,
        conf={ 'newBranch': default_args.get('branch') }
    )

    # The execution context is automatically passed by task.pre_execute method
    task_trigger.pre_execute = lambda context: LoggingMixin().log.info(
        'Branch name is: ' + "ok" + '_' \
        + context['ts_nodash'] \
        + ' and lakeFS URL is: ' + "ok" \
        + '/repositories/' + "ok" + '/objects?ref=' \
        + "ok" + '_' + context['ts_nodash'] )

    task_commit_etl_branch = LakeFSCommitOperator(
        task_id='commit_etl_branch',
        branch=default_args.get('branch'),
        msg='committing to lakeFS using airflow!',
        metadata={"committed_from": "airflow-operator"}
    )

    task_commit_etl_branch.post_execute = partial(print_commit_result, message='lakeFS commit id is: ')

    # Merge the changes back to the main branch.
    task_merge_etl_branch = LakeFSMergeOperator(
        task_id='merge_etl_branch',
        do_xcom_push=True,
        source_ref=default_args.get('branch'),
        destination_branch=default_args.get('default-branch'),
        msg='merging ' + default_args.get('branch') + ' to the ' + default_args.get('default-branch') + ' branch',
        metadata={"committer": "airflow-operator"}
    )

    task_merge_etl_branch.post_execute = partial(print_commit_result, message='lakeFS commit id is: ')

    task_create_etl_branch >> task_trigger >> task_commit_etl_branch >> task_merge_etl_branch
    
sample_workflow_dag = lakefs_wrapper_dag()



###################################################################



#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


# [START tutorial]
# [START import_module]
import json

import pendulum

from airflow.decorators import dag, task

# [END import_module]

# [START of lakeFS Code]
from airflow.models import Variable
import io
from airflow.operators.python import get_current_context
import lakefs_client
from lakefs_client.client import LakeFSClient
# lakeFS credentials and endpoint
configuration = lakefs_client.Configuration()
configuration.username = Variable.get("lakefsAccessKey")
configuration.password = Variable.get("lakefsSecretKey")
configuration.host = Variable.get("lakefsEndPoint")
client = LakeFSClient(configuration)
# [END of lakeFS Code]

# [START instantiate_dag]
@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=['example'],
)
def lakefs_tutorial_taskflow_api_etl():
    """
    ### TaskFlow API Tutorial Documentation
    This is a simple ETL data pipeline example which demonstrates the use of
    the TaskFlow API using three simple tasks for Extract, Transform, and Load.
    Documentation that goes along with the Airflow TaskFlow API tutorial is
    located
    [here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html)
    """
    # [END instantiate_dag]

    # [START extract]
    @task()
    def extract():
        """
        #### Extract task
        A simple Extract task to get data ready for the rest of the data
        pipeline. In this case, getting data is simulated by reading from a
        hardcoded JSON string.
        """
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'

        order_data_dict = json.loads(data_string)
        return order_data_dict

    # [END extract]

    # [START transform]
    @task(multiple_outputs=True)
    def transform(order_data_dict: dict):
        """
        #### Transform task
        A simple Transform task which takes in the collection of order data and
        computes the total order value.
        """
        total_order_value = 0

        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}

    # [END transform]

    # [START load]
    @task()
    def load(total_order_value: float):
        """
        #### Load task
        A simple Load task which takes in the result of the Transform task and
        instead of saving it to end us  er review, just prints it out.
        """

        print(f"Total order value is: {total_order_value:.2f}")

        # [START of lakeFS Code]
        repo = default_args['repo']
        context = get_current_context()
        newBranch = context["dag_run"].conf["newBranch"]
        contentToUpload = io.BytesIO(f"Total order value is: {total_order_value:.2f}".encode('utf-8'))
        client.objects.upload_object(
            repository=repo,
            branch=newBranch,
            path="total_order_value.txt", content=contentToUpload)
        # [END of lakeFS Code]

    # [END load]

    # [START main_flow]
    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])
    # [END main_flow]


# [START dag_invocation]
tutorial_etl_dag = lakefs_tutorial_taskflow_api_etl()
# [END dag_invocation]

# [END tutorial]