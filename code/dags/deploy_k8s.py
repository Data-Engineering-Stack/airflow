from kubernetes.client import models as k8s
import sys
from airflow.models import Variable


def get_executor_config():
    executor_config = {
        "pod_override": k8s.V1Pod(
            metadata=k8s.V1ObjectMeta(
            labels={ "spark" : "driver"}
            )
        ),
        spec = k8s.V1PodSpec(
        set_hostname_as_fqdn=True,
        containers=[
            k8s.V1Container(
                name="base",
                image="maxvan112/airflow-amin",
                ports=[k8s.V1ContainerPort(container_port=4040),k8s.V1ContainerPort(container_port=7337)]
                + [k8s.V1ContainerPort(container_port=port) for port in range(42000,42049)],
                env=[
                    k8s.V1EnvVar(name="PYSPARK_PYTHON",
                                 value="/opt/bitname/python/bin/python"
                                 ),
                    k8s.V1EnvVar(name="SPARK_HOME",
                                 value="/home/airflow/.local/lib/python3.8/site-packages/pyspark"
                                 ),
                    k8s.V1EnvVar(name="PYSPARK_DRIVER_PYTHON",value=sys.executable)
                ],
            )
        ],
        ),
        
    }
    return executor_config

executor_config = get_executor_config()