from __future__ import (print_function)
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger
import time
import yaml
from kubernetes import client, config, utils
from kubernetes.watch import Watch
from kubernetes.client.rest import ApiException

class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()
    def start_kube_job(self, kubeconfig_path, yaml_path, namespace="default"):

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

    def monitor_kube_job(self,kubeconfig_path, job_name, namespace="default"):
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

    def extension_start(self, fields):
        kubeconfig = str(fields.get("config"))
        job_yaml = str(fields.get("yaml"))
        namespace = str(fields.get("namespace"))
        print(kubeconfig)
        print(job_yaml)
        print(namespace)
        #get_pods(kubeconfig, namespace="dev")
        job = self.start_kube_job(kubeconfig, job_yaml, namespace)
        self.monitor_kube_job(kubeconfig, job, namespace)

        # Return the result with a payload containing a Hello message...
        return ExtensionResult(
            unv_output=''
        )
