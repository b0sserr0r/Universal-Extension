#!/opt/universal/python/bin/python
# --
#         Origins: Stonebranch
#          Author: Ravi Kumar Murugesan
#            Date: 11-MAY-2022
#
#    Copyright (c) Stonebranch, 2022.  All rights reserved.
#
# --
version = "1.0"
purpose = "Kubernetes"
# --
#           Version History:    1.0     Ravi M     03-MAY-2022     Initial Version
# --
import time
import subprocess
import argparse
import sys
import logging,os
#logging.basicConfig(level="${ops_kube_log_level}", format=' %(asctime)s - %(levelname)s - %(message)s')
#kubernetes_config_file_path = r"${ops_kube_config_file}"
####Get input parameters


def ScriptSetup():
    parser=argparse.ArgumentParser(description='Purpose : Trigger Kubernetes Cron job')
    
    # ## --> Capture Universal Task Form Variables Here
    #parser.add_argument("--config_file", default=r"${ops_kube_config_file}")
    parser.add_argument('--job_name', default="")
    parser.add_argument('--namespace', default="}")
    parser.add_argument('--yaml_file', default="")
                                                  
    parser.add_argument('--fetch_logs', default='')
    parser.add_argument('--monitor_job', default='')
    parser.add_argument('--delete_job', default='')
    # ## --
    global args
    args = parser.parse_args()
    # ## --> Logging info
    parser.add_argument("--logginglevel", default="info")
    logging.info("Executing version " + version + " with the following paramaters")
    logging.info(args)
    args.yaml_file = "D:\\Kubernetes\\Job Yaml\\Job1.yaml"
    args.job_name = "pi"
    args.monitor_job = "true"
    args.fetch_logs = "true"
    args.namespace = "dev"
# --
##
##
def create_job():
    logging.info("Attempting to create Job")
    try:
        create_cmd="kubectl apply -f "+'"'+args.yaml_file+'"' + " -n " + args.namespace
        logging.info("create command:"+str(create_cmd))
        create_log = subprocess.check_output(create_cmd,shell=True)
        logging.info(str(create_log))
        expected_out="job.batch/"+args.job_name+" created"
        if f"""{expected_out}""" in f"""{create_log}""":
            logging.info("Job Created successfully:"+str(create_log))
        else:
            logging.error("Issues in job creation : "+str(create_log))
    except Exception as e:
        logging.error("Error creating the job:"+str(e))
        sys.exit(1) 
#
######################################################
# Monitor kubernetes Job
######################################################
def monitor_job():
    logging.info("Monitoring the Job")
    try:
        monitor_cmd="kubectl wait --for=condition=complete --timeout=300s job/"+args.job_name + " -n " + args.namespace
        logging.info("monitor job command:"+str(monitor_cmd))
        kube_job_logs = os.system(monitor_cmd)
        logging.info(kube_job_logs)
        if kube_job_logs == 0:
            logging.info("Get the status")
            status_command="kubectl get job "+args.job_name+" -o jsonpath='{"+".status.succeeded}'" + " -n " + args.namespace
            logging.info("Job Status:"+str(status_command))
            job_status = subprocess.check_output(status_command,shell=True)
            logging.info("Job status:"+str(job_status))
            job_status_decode=job_status.decode("utf-8") 
            #print("variable type",type(job_status_decode))
            logging.info("Job status"+str(job_status_decode))
            if job_status_decode == "'1'":
                job_status="success"
            else:
                job_status="failed"
            return job_status
        else:
            logging.debug("Job status :"+str(job_status))
    except Exception as e:
        logging.error("Error Monitoring execution : "+str(e))
        sys.exit(1) 

#
######################################################
# Delete kubernetes Job
######################################################
def delete_job():
    try:
        delete_command="kubectl delete jobs/"+args.job_name + " -n " + args.namespace
        logging.debug(delete_command)
        delete_status=os.system(delete_command)
        if delete_command ==0:
            logging.info("Job deleted. status='%s'" % str(delete_status))
        else:
            logging.info(str(delete_command))
    except Exception as e:     
        logging.error("Error Calling delete job : {0}".format(sys.exc_info()))
        sys.exit(1) 

###########################################################
# Main Function 
###########################################################
def main():
    ScriptSetup()
    #print(str(args.yaml_file))
    
    ##set context
    #
    #ibm_login="ibmcloud login --apikey fMcmxyo3kT6tFGMTYg09y31XG9vFMqsJCAUqDiyN5SF1 -r jp-tok"
    #ibm_login_exec=os.system(ibm_login)
    #logging.info("login response:"+str(ibm_login_exec))
    #cluster_config="ibmcloud ks cluster config --cluster cluster-bot-dltbnd-gw-dev"
    #kube_config = os.system(cluster_config)
    #logging.info(str(kube_config))
    create_job()
    job_status=""
    if args.monitor_job == "true":
        job_status = monitor_job()

    ###########Fetch logs based on Job definition input
    if args.fetch_logs == "true":
        logging.info("Fetch Output for the job")
        try:
            fetch_log_command=f"kubectl logs job.batch/{args.job_name}" + " -n " + args.namespace
            logging.debug("Command to get job output:"+str(fetch_log_command))
            kube_job_logs = os.system(fetch_log_command)
            print(kube_job_logs)
        except Exception as e:
            logging.error("Error While fetching the logs ,Check Kubectl access"+str(e))
     ###########Delete the job based on Job definition input
    if args.delete_job =="true":
        delete_job()
    ########################################################################
    ##### Set the Job status in universal controller##########################
    if job_status=="success":
        logging.info("Status set to success in Universal controller")
        sys.exit(0)
    elif job_status=="failed":
        logging.info("Status set to Failed in Universal controller")
        sys.exit(10)
    else:
        if monitor_job == "false":
            logging.info("Monitoring Not enabled")
        

# -- Main Logic Function
if __name__ == '__main__':
    main()