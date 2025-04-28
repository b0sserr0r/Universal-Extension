
import requests
import time
def main():
    login_dict = login()
    token = login_dict["token"]
    botname = "Create Excel"
    botid = 15574207
    boitid_str = str(botid)
    deployid = exec_bot(str(login_dict["token"]),boitid_str,"792318")
    print("Deployment ID : " + str(deployid))
    monitor_exec_bot(login_dict["token"],deployid)



def login():
    url = "https://community.cloud.automationanywhere.digital/v2/authentication"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "username": "parinya.c@askme.co.th",
        "password": "11092537@Boss",
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
        print("Failed to log on:", response.status_code)
        print("Response:", response.text)
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
        automationname = data["automationName"]
        return automationname
        
    else:
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
        "field": "automationName"
                }
        }
    #time.sleep(5)
    while True:
        response = requests.post(url, headers=headers,json=data, verify=False)
        if response.status_code == 200:
            data = response.json()
            status = data["list"][0]["status"]
            progress = int(data["list"][0]["progress"])
            print("Waiting for finish....")
            #logger.info("Status : " + status)
            # if(progress == 100):
            #     if(status == "RUN_FAILED"):
            #         message = data["list"][0]["message"]
            #         print("Bot Run Failed : " + message)
            #         #logger.info("Bot Error : " + message)
            #     else:
            #         print("Bot Run Succussfull!")
            #     break
            # else:
            #     time.sleep(2)
                    
        else:       
            return None 
main()