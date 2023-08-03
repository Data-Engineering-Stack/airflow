from kubernetes.client import models as k8s

def create_executor_config():
    executor_config = {
        "pod_override": k8s.V1Pod(
            metadata=k8s.V1ObjectMeta(
            labels={
                    ""
        }
            )
        ),
        spec = k8s.V1PodSpec(
        set_hostname_as_fqdn=True,
        containers=[
            k8s.V1Container(
                name="base",
                image="",
                ports="",
                env=[
                    k8s.V1EnvVar("")
                ]
            )
        ]
        )
    }
    return executor_config
