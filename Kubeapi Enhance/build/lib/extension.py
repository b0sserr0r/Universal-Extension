from __future__ import print_function
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger
import time
import yaml
from kubernetes import client, config, utils
from kubernetes.watch import Watch
from kubernetes.client.rest import ApiException
import sys

class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension"""

    def __init__(self):
        """Initializes an instance of the 'Extension' class"""
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
                logger.debug(f"Created {kind} '{name}'")
                print(f"Created {kind} '{name}'")
            except ApiException as e:
                logger.error(f"Failed to create {kind}: {e}")
                print(f"Failed to create {kind}: {e}")
        
        if not job_name:
            logger.error("No Job definition found in the YAML.")
            raise ValueError("No Job definition found in the YAML.")
            sys.exit(1)

        return job_name

    def monitor_kube_job(self, kubeconfig_path, job_name, namespace="default"):
        """Monitors the specified Kubernetes Job and prints its logs after completion."""
        config.load_kube_config(config_file=kubeconfig_path)
        batch_v1 = client.BatchV1Api()
        logger.debug(f"Monitoring Job '{job_name}' in namespace '{namespace}'...")
        print(f"Monitoring Job '{job_name}' in namespace '{namespace}'...")
        w = Watch()
        for event in w.stream(batch_v1.list_namespaced_job, namespace=namespace, timeout_seconds=300):
            job = event['object']
            if job.metadata.name != job_name:
                continue
            if job.status.succeeded:
                logger.debug(f"Job '{job_name}' completed successfully.")
                print(f"Job '{job_name}' completed successfully.")
                w.stop()
            elif job.status.failed:
                logger.debug(f"Job '{job_name}' failed.")
                print(f"Job '{job_name}' failed.")
                w.stop()
        
    
    def fetch_kube_log(self, kubeconfig_path, job_name, namespace="default"):
        """Fetches and prints logs from the pod(s) created by the given Kubernetes Job."""
        config.load_kube_config(config_file=kubeconfig_path)
        core_v1 = client.CoreV1Api()

        pods = core_v1.list_namespaced_pod(namespace, label_selector=f"job-name={job_name}")
        for pod in pods.items:
            pod_name = pod.metadata.name
            logger.debug(f"Job '{job_name}' failed.")
            print(f"Logs from pod '{pod_name}':\n")
            try:
                log = core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
                logger.debug(f"Logs from pod {pod_name} : {log}")
                print(f"Logs from pod {pod_name} : {log}")
            except ApiException as e:
                logger.error(f"Could not fetch logs for pod '{pod_name}': {e}")
                print(f"Could not fetch logs for pod '{pod_name}': {e}")
                sys.exit(1) 

    def delete_kube_job(self, kubeconfig_path, job_name, namespace="default"):
        """Deletes the Kubernetes Job and its pods."""
        config.load_kube_config(config_file=kubeconfig_path)
        batch_v1 = client.BatchV1Api()
        core_v1 = client.CoreV1Api()
        logger.debug(f"Deleting Job '{job_name}' and its pods...")
        print(f"Deleting Job '{job_name}' and its pods...")
        delete_opts = client.V1DeleteOptions(propagation_policy='Foreground')

        try:
            batch_v1.delete_namespaced_job(
                name=job_name,
                namespace=namespace,
                body=delete_opts
            )
            logger.debug(f"Job '{job_name}' deletion initiated.")
            print(f"Job '{job_name}' deletion initiated.")
        except ApiException as e:
            print(f"Failed to delete job '{job_name}': {e}")
            logger.error(f"Failed to delete job '{job_name}': {e}")
            sys.exit(1)

    def extension_start(self, fields):
        kubeconfig = str(fields.get("config"))
        job_yaml = str(fields.get("yaml"))
        namespace = str(fields.get("namespace"))
        print(f"Start Kuberbetes Job...")
        print(f"File Config {kubeconfig}")
        print(f"File Yaml {job_yaml}")
        print(f"Namespace {namespace}")

        logger.debug(f"Start Kuberbetes Job...")
        logger.debug(f"File Config {kubeconfig}")
        logger.debug(f"File Yaml {job_yaml}")
        logger.debug(f"Namespace {namespace}")
        # print(kubeconfig)
        # print(job_yaml)
        # print(namespace)

        job = self.start_kube_job(kubeconfig, job_yaml, namespace)

        fetch_log = str(fields.get("fetch_log"))
        delete_job = str(fields.get("delete_job"))
        self.monitor_kube_job(kubeconfig, job, namespace)
        if fetch_log == 'True':
           self.fetch_kube_log(kubeconfig, job, namespace)
        if delete_job == 'True':
           self.delete_kube_job(kubeconfig, job, namespace)
        return ExtensionResult(
            unv_output=''
        )
