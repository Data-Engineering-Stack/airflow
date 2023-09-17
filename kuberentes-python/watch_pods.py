from kubernetes import client, config, watch
import time
import requests

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


v1 = client.CoreV1Api()
# print("Listing pods with their IPs:")
# ret = v1.list_pod_for_all_namespaces(watch=False)
# for i in ret.items:
#     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

namespace = 'airflow'
pod_name_prefix = "airflow-"

def send_alert(pod_name):
    raise Exception(f"{pod_name} failed!")


def monitor_specific_pods(namespace, pod_name_prefix):
    w = watch.Watch()

    # Use a generator to watch for pod events
    for event in w.stream(v1.list_namespaced_pod, namespace=namespace):
        pod = event['object']
        pod_name = pod.metadata.name
        pod_phase = pod.status.phase

        # Check if the pod name starts with the specified prefix
        if pod_name.startswith(pod_name_prefix):
            print(f"Pod Name: {pod_name}, Phase: {pod_phase}")
            if pod_phase == "Failed":
                # Send an alert when the pod fails
                send_alert(pod_name)
            print(f"Pod Name: {pod_name}, Phase: {pod_phase}")

try:
    monitor_specific_pods(namespace, pod_name_prefix)
except KeyboardInterrupt:
    print("Monitoring stopped.")