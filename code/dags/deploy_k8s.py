from kubernetes.client import models as k8s
import sys
from airflow.models import Variable


#https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/kubernetes.html
def get_executor_config():

    # Kubernetes executor config
    labels = {
        "spark": "driver",
        "airflow": "spark",
    }
    executor_config = {
        "pod_override": k8s.V1Pod(
        metadata=k8s.V1ObjectMeta(labels=labels),
        spec=k8s.V1PodSpec(
        set_hostname_as_fqdn=True,
        containers=[
            k8s.V1Container(
                name="base",
                image="maxvan112/airflow-amin:1.8",
                ports=[k8s.V1ContainerPort(container_port=4040),k8s.V1ContainerPort(container_port=7337)]
                + [k8s.V1ContainerPort(container_port=port) for port in range(42000,42049)],
                env=[
                    k8s.V1EnvVar(name="JAVA_HOME",
                                 value="/usr/lib/jvm/java-11-openjdk-amd64/"
                                 ),
                    k8s.V1EnvVar(name="SPARK_HOME",
                                 value="/home/airflow/.local/lib/python3.10/site-packages/pyspark"
                                 ),
                    k8s.V1EnvVar(name="PYSPARK_DRIVER_PYTHON",value=sys.executable),
                ],
            )
        ],
    ),
    )
}
    return executor_config

executor_config = get_executor_config()













def get_spark_config():


    spark_conf = {
        "spark.driver.maxResultSize": "1g",
        "spark.driver.port": "42000",
        "spark.port.maxRetries": "16",
        "spark.driver.host": "{{ task_instance.hostname }}.airflow",
        "spark.driver.blockManager.port": "42016",
        "spark.blockManager.port": "42032",
        "spark.sql.execution.pyarrow.enabled": "true",
        "spark.sql.timestampType": "TIMESTAMP_NTZ",
        "spark.sql.legacy.timeParserPolicy": "CORRECTED",
        "spark.scheduler.mode": "FAIR",
        "spark.sql.adaptive.enabled": "true",
        "spark.shuffle.service.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.dynamicAllocation.enabled": "true",
        "spark.dynamicAllocation.shuffleTracking.enabled": "true",
        "spark.dynamicAllocation.maxExecutors":"2",
        "spark.executor.memory":"1g"
    }


    return spark_conf