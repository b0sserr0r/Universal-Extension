import time
import yaml
from kubernetes import client, config, utils
from kubernetes.watch import Watch
from kubernetes.client.rest import ApiException


def start_kube_job(kubeconfig_path, yaml_path, namespace="default"):
    """Creates a Kubernetes Job from a YAML file."""
    config.load_kube_config(config_file=kubeconfig_path)
    api_client = client.ApiClient()

    job_name = None

    with open(yaml_path) as f:
        docs = list(yaml.safe_load_all(f))

    for doc in docs:
        kind = doc.get("kind")
        metadata = doc.get("metadata", {})
        name = metadata.get("name")
        if kind == "Job":
            job_name = name
        try:
            utils.create_from_dict(api_client, data=doc, namespace=namespace)
            print(f"✅ Created {kind} '{name}'")
        except ApiException as e:
            print(f"❌ Failed to create {kind}: {e}")

    if not job_name:
        raise ValueError("No Job definition found in the YAML.")

    return job_name


def monitor_kube_job(kubeconfig_path, job_name, namespace="default"):
    """Monitors the specified Kubernetes Job and prints its logs after completion."""
    config.load_kube_config(config_file=kubeconfig_path)
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()

    print(f"🔍 Monitoring Job '{job_name}' in namespace '{namespace}'...")
    w = Watch()
    for event in w.stream(batch_v1.list_namespaced_job, namespace=namespace, timeout_seconds=300):
        job = event['object']
        if job.metadata.name != job_name:
            continue
        if job.status.succeeded:
            print(f"✅ Job '{job_name}' completed successfully.")
            w.stop()
        elif job.status.failed:
            print(f"❌ Job '{job_name}' failed.")
            w.stop()

    # Fetch logs from the associated pod
    pods = core_v1.list_namespaced_pod(namespace, label_selector=f"job-name={job_name}")
    for pod in pods.items:
        pod_name = pod.metadata.name
        print(f"📄 Logs from pod '{pod_name}':\n")
        try:
            log = core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
            print(log)
        except ApiException as e:
            print(f"⚠️ Could not fetch logs for pod '{pod_name}': {e}")

def get_pods(kubeconfig_path, namespace="default", label_selector=None):
    """
    Lists pods in the specified namespace using the provided kubeconfig.
    
    :param kubeconfig_path: Path to kubeconfig file
    :param namespace: Namespace to query pods from
    :param label_selector: Optional label selector string (e.g., 'app=myapp')
    """
    config.load_kube_config(config_file=kubeconfig_path)
    core_v1 = client.CoreV1Api()

    try:
        pods = core_v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector or ""
        )
        print(f"📦 Found {len(pods.items)} pod(s) in namespace '{namespace}':")
        for pod in pods.items:
            print(f"- {pod.metadata.name} (Status: {pod.status.phase})")
    except ApiException as e:
        print(f"❌ Error fetching pods: {e}")
# Example usage:
if __name__ == "__main__":
    kubeconfig = "D:\\Kubernetes\\Config\\minikube.yaml"
    job_yaml = "D:\\Kubernetes\\Job Yaml\\Job1.yaml"
    namespace = "dev"
    #get_pods(kubeconfig, namespace="dev")
    job = start_kube_job(kubeconfig, job_yaml, namespace)
    monitor_kube_job(kubeconfig, job, namespace)
