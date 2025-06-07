from __future__ import (print_function)
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger
from universal_extension.deco import dynamic_choice_command
import requests
#import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import base64
import os

session_id= ""
job_list = []
job_id = ""
job_dict = {}
taskid = ""
enterprise_url = ""
url_backup_session = ""
token = ""
# df = pd.DataFrame()
# df['Job Name'] = None
# df['State'] = None
# df['Result'] = None


class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()


    # def LogOn(fields):
    #     global enterprise_url
    #     url = enterprise_url + "/api/sessionMngr/?v=latest"
    #     user = str(fields.get("credential")["user"])
    #     password = str(fields.get("credential")["password"])
    #     token = util.encodebase64(user + ":" + password)
    #     headers = {
    #     'Accept': 'application/json',
    #     'Authorization': 'Basic ' + token
    #     }

    #     response = requests.post(url, headers=headers, verify=False)

    #     if response.status_code == 201:
    #         data = response.json()
    #         #session_id = data.get("SessionId")
    #         #session_id = response.headers.get('X-RestSvcSessionId')

    #         return response.headers.get('X-RestSvcSessionId')
    #     else:
    #         print("Failed to log on:", response.status_code)
    #         print("Response:", response.text)
    #         return None
        
    def ListJob(self):
        global session_id, job_dict, enterprise_url
        print("List Job Session : " + session_id)
        url = enterprise_url + "/api/Jobs"
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'X-RestSvcSessionId': str(session_id)
        }
        response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            data = response.json()
            #job_dict = {ref["Name"]: ref["UID"] for ref in data["Refs"]}
            return [ref["Name"] for ref in data["Refs"]]

        else:
            print("Failed to log on:", response.status_code)
            print("Response:", response.text)
            return None


    @dynamic_choice_command("job_list")
    def job_list(self, fields):
        global session_id, job_list, enterprise_url
        enterprise_url = str(fields.get('enterprise_manager_url')) #"https://172.16.1.120:9398"
        user = str(fields.get("credential")["user"])
        password = str(fields.get("credential")["password"])
        token = util.encodebase64(user + ":" + password)
        session_id = util.LogOn(token) 
        job_lists = self.ListJob()
        return ExtensionResult(
                rc=0,
                message="Values for choice field: 'jobs_list'",
                values=job_lists
                ) 

    def get_job_uid(self):
         global session_id, job_dict, enterprise_url
         url = enterprise_url + "/api/Jobs"
         headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'X-RestSvcSessionId': str(session_id)
         }
         response = requests.get(url, headers=headers, verify=False)

         if response.status_code == 200:
            data = response.json()
            return {ref["Name"]: ref["UID"] for ref in data["Refs"]}
         else:
            print("Failed to log on:", response.status_code)
            print("Response:", response.text)
            return None

    def StartJob(self):
        global session_id, job_id, taskid, enterprise_url
        url = enterprise_url + "/api/jobs/" + job_id + "?action=start"
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'X-RestSvcSessionId': str(session_id)
        }
        response = requests.post(url, headers=headers, verify=False)

        if response.status_code == 202:
            data = response.json()
            #print(str(data))
            taskid = data.get("TaskId")
            self.GetTaskStatus()

        else:
            print("Failed to log on:", response.status_code)
            print("Response:", response.text)
            return None
    def GetTaskStatus(self):
        global session_id, taskid, enterprise_url, url_backup_session, token
        url = enterprise_url + "/api/tasks/" + taskid

   
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic ' + token,
            'X-RestSvcSessionId': str(session_id),
        }

        while True:
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                state = data.get("State", "")
                

                if state == "Finished":
                    print("Job state : ", state)
                    url_backup_session = data["Links"][1]["Href"]
                    self.GetBackupDetail()
                    break
                else:
                    print("Job state : ", state)
                    time.sleep(2) 
            else:
                print("Failed to get task status:", response.status_code)
                print("Response:", response.text)
                break
    def GetBackupDetail(self):
        global session_id, url_backup_session, token
        url = url_backup_session
    
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic ' + token,
            'X-RestSvcSessionId': str(session_id),
        }

        while True:
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                jobname = data.get("JobName", "")
                state = data.get("State", "")
                result = data.get("Result", "")

                if state == "Stopped":
                    # df.loc[1, 'Job Name'] = jobname
                    # df.loc[1, 'State'] = state
                    # df.loc[1, 'Result'] = result
                    print("Job run result " + jobname  +" is " + state + " " + result)
                    print("Job ")
                    #print(str(df))
                    os._exit(1)
                    break
                elif state == "Success":
                     print("Job run result " + jobname  +" is " + state + " " + result)
                else:
                    time.sleep(1)
            else:
                print("Failed to log on:", response.status_code)
                print("Response:", response.text)
                os._exit(1)
                #return None

    def extension_start(self, fields):
        global session_id, job_list, job_id, job_dict, enterprise_url, token

        enterprise_url = str(fields.get('enterprise_manager_url'))
        user = str(fields.get("credential")["user"])
        password = str(fields.get("credential")["password"])
        token = util.encodebase64(user + ":" + password)
        session_id = util.LogOn(token) 
        # session_id = self.LogOn() 
        # print("Session " + session_id)
        # job_list = self.ListJob()
        # print("Job List " + job_list)
        function = fields.get('function', [])

        if(function[0] == "Start Job"):
            job_dict = self.get_job_uid()                   
            #print("Job Dict : "+ str(job_dict))
            jobname = fields.get('job_list', [])
            #print("Job Name : "+ jobname[0])
            job_id = job_dict.get(jobname[0])   
            print("Job Name : "+ str(jobname[0]))   
            print("Job UID : "+ str(job_id))   
            self.StartJob()
            
        
        return ExtensionResult(
            unv_output=""
        )
    
class util:
    def encodebase64(str_encode):
        encoded_bytes = base64.b64encode(str_encode.encode("utf-8"))
        encoded_str = encoded_bytes.decode("utf-8")
        return str(encoded_str)
    def LogOn(token):
        global enterprise_url
        url = enterprise_url + "/api/sessionMngr/?v=latest"
        headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ' + token
        }

        response = requests.post(url, headers=headers, verify=False)

        if response.status_code == 201:
            data = response.json()
            #session_id = data.get("SessionId")
            #session_id = response.headers.get('X-RestSvcSessionId')

            return response.headers.get('X-RestSvcSessionId')
        else:
            print("Failed to log on:", response.status_code)
            print("Response:", response.text)
            return None