# a python script to send server notice to users on a matrix synapse server
# 29-Apr-2024
# github.com/iamtalhaasghar

import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

# Define your access token, target user ID, server domain, server URL
access_token = os.getenv('ACCESS_TOKEN')
server_url = os.getenv('SERVER_URL')
api_url = f"{server_url}/_synapse/admin/v1/send_server_notice"
msg = os.getenv('MSG')

def send_notice(target_user, msg):
    
    # Construct the request payload
    payload = {
        "user_id": target_user,
        "content": {
            "msgtype": "m.text",
            "body": msg
        }
    }

    # Construct headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        # Send the POST request
        response = requests.post(api_url, json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Server notice sent successfully to {target_user}")
        else:
            print(f"Failed to send server notice to {target_user}. Status code: {response.status_code}")
            print("Response content:", response.content)
    except Exception as e:
        print(e)

def send_beta_invitation():
    server_domain = server_url.replace('https://', '')
    users = [i.strip() for i in open('beta_users.csv').readlines()][40:]
    users = ['@'+i.replace('@', '-')[:-8]+f':{server_domain}' for i in users]
    for u in users:
        print('Sending notice to:', u)
        send_notice(u, msg)
        time.sleep(1)

if __name__=="__main__":
    send_beta_invitation()
