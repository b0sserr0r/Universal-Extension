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

    def create_job(self,fields):
        print("Attempting to create Job")
        logger.debug("Attempting to create Job")
        yaml_file = str(fields.get('yaml_file'))
        job_name = str(fields.get('jobname'))
        namespace = str(fields.get('namespace'))
        try:
        
            create_cmd="kubectl apply -f " + yaml_file + " -n " + namespace
            logger.debug("create command:"+str(create_cmd))
            #print("create command:"+str(create_cmd))
            create_log = subprocess.check_output(create_cmd,shell=True)
            logger.debug(str(create_log))
            print(str(create_log))
            expected_out="job.batch/"+ job_name+" created"
            if f"""{expected_out}""" in f"""{create_log}""":
                print("Job Created successfully: " + str(create_log))
                logger.debug("Job Created successfully: "+str(create_log))
                self.monitor_job(job_name,namespace)
            else:
                logger.error("Issues in job creation : "+str(create_log))
                os._exit(1)
        except Exception as e:
            logger.error("Error creating the job:"+str(e))
            os._exit(1)
            #raise SystemExit(1)

    def monitor_job(self,job_name,namespace):
        logger.debug("Monitoring the Job")
        try:
            #--timeout=300s
            monitor_cmd="kubectl wait --for=condition=complete job/"+ job_name + " -n " + namespace
            logger.debug("monitor job command:"+str(monitor_cmd))
            kube_job_logs = os.system(monitor_cmd)
            logger.debug(kube_job_logs)
            if kube_job_logs == 0:
                logger.debug("Get the status")
                print("Get the status")
                status_command="kubectl get job "+job_name+" -o jsonpath='{"+".status.succeeded}'" + " -n " + namespace
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
            

    def delete_job(self,job_name,namespace):
        try:
            delete_command="kubectl delete jobs/"+job_name + " -n " + namespace
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
        

    def extension_start(self, fields):
        job_name = str(fields.get('jobname'))
        monitorjob = str(fields.get('monitor_job'))
        fetch_logs = str(fields.get('fetch_log'))
        delete_job = str(fields.get('delete_job'))
        namespace = str(fields.get('namespace'))

        if delete_job == "True":
            getjob = ["kubectl", "get", "job", job_name , "-n", namespace]
            result = subprocess.run(getjob, capture_output=True, text=True)
            if "not found" in result.stderr.lower() or "not found" in result.stdout.lower():
                print("Not found existing job : " + job_name)
            else:
                self.delete_job(job_name,namespace)
        self.create_job(fields)
        job_status = ""
        print("Monitor : " + monitorjob)
        if monitorjob == "True":
           job_status = self.monitor_job(job_name,namespace)
    
        if fetch_logs == "True":
           logger.debug("Fetch Output for the job")
           print("Fetch Output for the job")
           try:
              fetch_log_command=f"kubectl logs job.batch/{job_name} -n " + namespace
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
