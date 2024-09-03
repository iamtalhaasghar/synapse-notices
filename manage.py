# a python script to send server notice to users on a matrix synapse server
# 29-Apr-2024
# github.com/iamtalhaasghar

import os
import requests
from dotenv import load_dotenv
import time
from redis import Redis
import sys
from synapse_admin import User, Room
import random

load_dotenv()

# Define your access token, target user ID, server domain, server URL
access_token = os.getenv('ACCESS_TOKEN')
server_url = os.getenv('SERVER_URL')

conn = (server_url.replace('https://', ''), 443, access_token, 'https://') 

rdb = Redis(decode_responses=True)

def send_notice(target_user, msg):
    api_url = f"{server_url}/_synapse/admin/v1/send_server_notice"
    
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

def add_user_to_room(target_user, room):
    api_url = f"{server_url}/_synapse/admin/v1/join/{room}"
    
    # Construct the request payload
    payload = {
        "user_id": target_user,
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
            print(f"Successfully added {target_user} to {room}")
        else:
            print(f"Failed to send server notice to {target_user}. Status code: {response.status_code}")
            print("Response content:", response.content)
    except Exception as e:
        print(e)

def send_beta_invitation():
    msg = os.getenv('MSG')
    server_domain = server_url.replace('https://', '')
    users = [i.strip() for i in open('beta_users.csv').readlines()][40:]
    users = ['@'+i.replace('@', '-')[:-8]+f':{server_domain}' for i in users]
    for u in users:
        print('Sending notice to:', u)
        send_notice(u, msg)
        time.sleep(1)

def invite_everyone_to_a_room(room_id):
    user = User(*conn)
    all_members = user.lists(limit=10000)
    # convert all_members list to dict so its easy to search a user by his id
    all_members = {u['name'] :  u for u in all_members}
    room = Room(*conn)
    existing_members = room.list_members(room_id)
    non_members = list(set(all_members.keys()) - set(existing_members))
    print(len(non_members), 'have yet not joined this room.')
    for u in non_members:
        add_user_to_room(u, room_id)
        
def get_list_of_all_members():
    user = User(*conn)
    all_members = user.lists(limit=10000)
    # convert all_members list to dict so its easy to search a user by his id
    all_members = {u['name'] :  u for u in all_members}
    return all_members
if __name__=="__main__":
    #invite_everyone_to_a_room(os.getenv('ROOM_ID'))
    members = list(get_list_of_all_members().keys())
    

