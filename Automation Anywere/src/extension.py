from __future__ import (print_function)
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger
from universal_extension.deco import dynamic_choice_command
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time

class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()

    def extension_start(self, fields):

        bottype = str(fields.get('bot_type')[0])
        login_dict = util.login(str(fields.get("credential")["user"]),str(fields.get("credential")["password"]))
        #print("Token : " + str(login_dict["token"]))
        print("Bot Type : " + bottype)
        if(bottype == "Bot Task"): # Bot Task Type 
            botname = fields.get('bots_list', [])
            botid = util.get_bot_id(login_dict["token"],str(botname[0]))
            boitid_str = str("".join(botid))
            deployid = util.exec_bot(str(login_dict["token"]),boitid_str,str(login_dict["userid"]))
            print("Deployment ID : " + str(deployid))
            util.monitor_exec_bot(login_dict["token"],deployid)
        else: # Process Type
            processid = int(fields.get('process_id'))
            ref_id = util.exec_process(str(login_dict["token"]),processid)
            #print("Ref ID : " + str(ref_id))
            util.monitor_process(str(login_dict["token"]),ref_id)

        return ExtensionResult(
            unv_output=''
         )        
    
    @dynamic_choice_command("bots_list")
    def bots_list(self, fields):
       
        workspace_type = str(fields.get("work_space_type"))
        username = str(fields.get("credential")["user"])
        logger.info("Workspace Type:" + str(workspace_type))
        logger.info("Username :" + str(username))
        #ws_type = str("".join(workspace_type))
        
        ws_str = "private"
        if "private" in str(workspace_type):
            ws_str = "private"
        else:
            ws_str = "public"

        
        login_dict = util.login(str(fields.get("credential")["user"]),str(fields.get("credential")["password"]))
        url = 'https://community.cloud.automationanywhere.digital/v2/repository/workspaces/private/files/list'
       
        headers = {
        'Content-Type': 'application/json',
        'X-Authorization': login_dict["token"]
        }
        data = {

        } 

        response = requests.post(url, headers=headers,json=data, verify=False)
        if response.status_code == 200:
        
            data = response.json()
            bots_name = [item["name"] for item in data["list"] if item.get("type") == "application/vnd.aa.taskbot"]
            return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'Bot Name'",
                    values = bots_name
            )
        
        else:
            print("Failed to log on:", response.status_code)
            print("Response:", response.text)
            return None
          

        
class util:
    def login(username,password):
        url = "https://community.cloud.automationanywhere.digital/v2/authentication"
        headers = {
        'Content-Type': 'application/json'
    }
        data = {
        "username": username,
        "password": password,
        "multipleLogin": True
    } 

        response = requests.post(url, headers=headers,json=data, verify=False)
        if response.status_code == 200:
        
            data = response.json()
            token = data["token"]
            userid = data["user"]["id"]
            result_dict = {
                "token": token,
                "userid": userid
             }
            return result_dict
        else:
            #print("Failed to log on:", response.status_code)
            #print("Response:", response.text)
            logger.error(response.text)
            os._exit(1)
            return None

    def get_bot_id(token,botname):
        url = "https://community.cloud.automationanywhere.digital/v2/repository/workspaces/private/files/list"
        headers = {
        'Content-Type': 'application/json',
        'X-Authorization': token
        }
        data = {

        } 

        response = requests.post(url, headers=headers,json=data, verify=False)
        if response.status_code == 200:
        
            data = response.json()
            botid = [item["id"] for item in data["list"] if item["name"] == botname]
            return botid
        
        else:
            
            #print("Response:", response.text)
            logger.error(response.text)
            os._exit(1)
            return None
        
    def exec_bot(token,botid,userid):
        url = "https://community.cloud.automationanywhere.digital/v3/automations/deploy"
        headers = {
        'Content-Type': 'application/json',
        'X-Authorization': token
        }
        data = {
              "fileId": botid,
              "runAsUserIds": [userid],
              "overrideDefaultDevice": True
            } 

        response = requests.post(url, headers=headers,json=data, verify=False)
        if response.status_code == 200:
            data = response.json()
            deployid = data["deploymentId"]
            return deployid
        
        else:
            logger.error(response.text)
            os._exit(1)
            return None   

    def monitor_exec_bot(token,deployid):
        url = "https://community.cloud.automationanywhere.digital/v3/activity/list"
        headers = {
        'Content-Type': 'application/json',
        'X-Authorization': token
        }
        data = {
        "filter": {
        "operator": "eq",
        "value": deployid,
        "field": "deploymentId"
                }
        }
        while True:
            
            response = requests.post(url, headers=headers,json=data, verify=False)
            if response.status_code == 200:
                data = response.json()
                status = data["list"][0]["status"]
                progress = int(data["list"][0]["progress"])
                print("Waiting for finish....")
                #print("Status : " + status)
                #logger.info("Status : " + status)
                if(progress == 100):
                    if(status == "RUN_FAILED"):
                        message = data["list"][0]["message"]
                        logger.error("Bot Run Failed : " + message)
                        os._exit(1)
                        #logger.info("Bot Error : " + message)
                    else:
                        print("Bot Run Succussfull!")
                    # if(status == "COMPLETED"):
                    #     print("Bot Run Succussfull!")
                    break
                else:
                    data = {
                "filter": {
                "operator": "eq",
                "value": data["list"][0]["id"],
                "field": "id"
                }
            }
                    time.sleep(2)
                    
            else:
                logger.error(response.text)
                os._exit(1)
                return None 

    def exec_process(token,process_id):
        url = "http://community.cloud.automationanywhere.digital/aari/v2/requests/create"
        headers = {
        'Accept': 'application/json',
        'X-Authorization': token
        }

        data = {
            
            "processId": process_id
            
        }
        response = requests.post(url, headers=headers,json=data, verify=False)
        if response.status_code == 201:
            data = response.json()
            refid= data["ref"]
            return refid

        else:
            #print("Failed to log on:", response.status_code)
            logger.error(response.text)
            os._exit(1)
            return None
        
    def monitor_process(token,refid):
        url = "http://community.cloud.automationanywhere.digital/aari/v2/requests/ref/" + refid
        headers = {
        'Accept': 'application/json',
        'X-Authorization': token
        }

        while True:
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                status= data["status"]
                print("Process Status : " + status)
                #logger.info("Process Status : " + status)
                if(status == "SUCCESS"):
                    for tasks in data["steps"]:
                        print("Task : " + tasks["name"] + " is " + tasks["executionStatus"])
                        #logger.info("Task : " + tasks["name"] + " is " + tasks["executionStatus"])
                    break
                else:
                    time.sleep(1) 
                
            else:
                #print("Failed to log on:", response.status_code)
                logger.error(response.text)
                os._exit(1)
                return None
    

       
        