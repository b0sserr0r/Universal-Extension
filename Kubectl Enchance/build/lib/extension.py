from __future__ import (print_function)
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger

import sys
import os
import subprocess
class Extension(UniversalExtension):
  
    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()

    def create_job(self,fields,kubectl_prefix):
        self.get_kube_config(fields)
        print("Attempting to create Job")
        logger.debug("Attempting to create Job")
        yaml_file = str(fields.get('yaml_file'))
        job_name = str(fields.get('jobname'))
        namespace = str(fields.get('namespace'))
        try:
        
            create_cmd= kubectl_prefix +" apply -f " + yaml_file + " -n " + namespace
            logger.debug("create command:"+str(create_cmd))
            #print("create command:"+str(create_cmd))
            create_log = subprocess.check_output(create_cmd,shell=True)
            logger.debug(str(create_log))
            print(str(create_log))
            expected_out="job.batch/"+ job_name+" created"
            if f"""{expected_out}""" in f"""{create_log}""":
                print("Job Created successfully: " + str(create_log))
                logger.debug("Job Created successfully: "+str(create_log))
                #self.get_kube_config(fields)
                #self.monitor_job(job_name,namespace,kubectl_prefix)
            else:
                logger.error("Issues in job creation : "+str(create_log))
                os._exit(1)
        except Exception as e:
            logger.error("Error creating the job:"+str(e))
            os._exit(1)
            #raise SystemExit(1)

    def monitor_job(self,fields,job_name,namespace,kubectl_prefix):
        logger.debug("Monitoring the Job")
        try:
            #--timeout=300s
            monitor_cmd=kubectl_prefix + " wait --for=condition=complete job/"+ job_name + " -n " + namespace
            logger.debug("monitor job command:"+str(monitor_cmd))
            kube_job_logs = os.system(monitor_cmd)
            logger.debug(kube_job_logs)
            if kube_job_logs == 0:
                logger.debug("Get the status")
                print("Get the status")
                self.get_kube_config(fields)
                status_command=kubectl_prefix + " get job "+job_name+" -o jsonpath='{"+".status.succeeded}'" + " -n " + namespace
                logger.debug("Job Status: "+str(status_command))
                #print("Job Status:"+str(status_command))
                job_status = subprocess.check_output(status_command,shell=True)
                logger.debug("Job status: "+str(job_status))
                #print("Job status:"+str(job_status))
                job_status_decode=job_status.decode("utf-8") 
                #print("variable type",type(job_status_decode))
                logger.debug("Job status"+str(job_status_decode))
                #print("Job status "+str(job_status_decode))
                if str(job_status_decode) == "1":
                    job_status="success"
                    print("Job status " + str(job_status))
                else:
                    job_status="failed"
                    print("Job status "+str(job_status))
                return job_status
            else:
                logger.debug("Job status :"+str(job_status))
                print("Job status :"+str(job_status))
        except Exception as e:
            logger.error("Error Monitoring execution : "+str(e))
            os._exit(1)
            

    def delete_job(self,job_name,namespace,kubectl_prefix):
        try:
            delete_command= kubectl_prefix + " delete jobs/"+job_name + " -n " + namespace
            #logger.debug(delete_command)
            #print(delete_command)
            delete_status=os.system(delete_command)
            if delete_command ==0:
                logger.debug("Job deleted. status='%s'" % str(delete_status))
                print(delete_status)
            else:
                print(delete_command)
                logger.debug(str(1))
        except Exception as e:     
            logger.error(f"Error Calling delete job : {str(e)}")
            os._exit(1)
    def get_kube_config(self,fields):
        try:
            region = str(fields.get('kube_credential_region')["password"])
            access_key = str(fields.get('kube_credential_access_key')["password"])
            secret_key = str(fields.get('kube_credentia_secret_key')["password"])
            cluster_name = str(fields.get('cluster_name'))
            kube_config_path = str(fields.get('file_config'))

            #print(cluster_name)
            #print(kube_config_path)
            # print(region)
            # print(access_key)
            # print(secret_key)
            set_region = ["aws", "configure", "set", "region" , region]
            result_region = subprocess.run(set_region, capture_output=True, text=True)
            #print(result_region.stdout)  

            set_access_key = ["aws", "configure", "set", "aws_access_key_id" , access_key]
            result_access_key= subprocess.run(set_access_key, capture_output=True, text=True)
            #print(result_access_key.stdout)  

            set_secret_key = ["aws", "configure", "set", "aws_secret_access_key" , secret_key]
            result_secret_key = subprocess.run(set_secret_key, capture_output=True, text=True)


            update_kube_config = ["aws", "eks", "update-kubeconfig" , "--region", region , "--name", cluster_name , "--kubeconfig" ,kube_config_path]
            result_update_kube_config = subprocess.run(update_kube_config, capture_output=True, text=True)
            if result_update_kube_config.returncode == 0:
                print(result_update_kube_config.stdout) 
            else: 
                print(result_update_kube_config.stderr) 
                os._exit(1)
        except Exception as e:     
            logger.error(f"Error : {str(e)}")
            os._exit(1)
        

    def extension_start(self, fields):
        file_config = str(fields.get('file_config'))
        job_name = str(fields.get('jobname'))
        monitorjob = str(fields.get('monitor_job'))
        fetch_logs = str(fields.get('fetch_log'))
        delete_job = str(fields.get('delete_job'))
        namespace = str(fields.get('namespace'))
        

        kubectl_prefix = ""
        getjob=""
        if not file_config:
           kubectl_prefix = "kubectl"
           getjob = ["kubectl", "get", "job", job_name , "-n", namespace]
        else:
           kubectl_prefix = "kubectl --kubeconfig=" + file_config
           getjob = ["kubectl","--kubeconfig=" + file_config, "get", "job", job_name , "-n", namespace]



        if delete_job == "True": 
            #getjob = ["kubectl", "get", "job", job_name , "-n", namespace]
            
            result = subprocess.run(getjob, capture_output=True, text=True)
            if "not found" in result.stderr.lower() or "not found" in result.stdout.lower():
                print("Not found existing job : " + job_name)
            else:
                self.get_kube_config(fields)
                self.delete_job(job_name,namespace,kubectl_prefix)
        self.create_job(fields,kubectl_prefix)
        job_status = ""
        print("Monitor : " + monitorjob)
        if monitorjob == "True":
           self.get_kube_config(fields)
           job_status = self.monitor_job(fields,job_name,namespace,kubectl_prefix)
    
        if fetch_logs == "True":
           logger.debug("Fetch Output for the job")
           print("Fetch Output for the job")
           try:
              self.get_kube_config(fields)
              fetch_log_command=f"{kubectl_prefix} logs job.batch/{job_name} -n " + namespace
              logger.debug("Command to get job output:"+str(fetch_log_command))
              print("Command to get job output:"+str(fetch_log_command))
              kube_job_logs = os.system(fetch_log_command)
              print(kube_job_logs)
           except Exception as e:
              logger.error("Error While fetching the logs ,Check Kubectl access"+str(e))
        
        if job_status=="success":
            print("Status set to success in Universal controller")
            logger.debug("Status set to success in Universal controller")
            
        elif job_status=="failed":
            print("Status set to Failed in Universal controller")
            os._exit(1)
            logger.debug("Status set to Failed in Universal controller")
        else:
            if monitorjob == "false":
                print("Monitoring Not enabled")
                logger.debug("Monitoring Not enabled")

        return ExtensionResult(
            unv_output=''
        )
