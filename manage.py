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
from datetime import timedelta

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

def growth_projection():
    import pandas as pd
    import matplotlib.pyplot as plt
    from datetime import datetime
    from collections import Counter

    members = get_list_of_all_members()
    dates = list()
    for k,v in members.items():
        ts = datetime.fromtimestamp(v['creation_ts']/1000)
        dates.append(ts.strftime('%Y-%m-%d'))

    # Count occurrences of each date
    date_counts = Counter(dates)



    # Convert to a DataFrame for easier plotting
    df = pd.DataFrame(date_counts.items(), columns=['Date', 'Count'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')


    # Print header
    print("Date Counts Summary:\n")

    # Pretty print date counts
    for index, row in df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD
        count = row['Count']
        print(f"Date: {date_str} | Count: {count}")

    # Get today's date
    today = datetime.now()

    # Define the date range (last 10 days)
    ten_days_ago = today - timedelta(days=30)

    # Filter DataFrame for the last 10 days
    recent_df = df[df['Date'] >= ten_days_ago]

    # Count the number of users in the last 10 days
    recent_count = recent_df['Count'].sum()
    print(f"Number of users in the last 30  days: {recent_count}")

    # Define a specific start date
    specific_start_date = datetime(2024, 8, 26)  # Example start date

    # Filter DataFrame from a specific date onwards
    specific_df = df[df['Date'] >= specific_start_date]

    # Count the number of users from a specific date onwards
    specific_count = specific_df['Count'].sum()
    print(f"Number of users from {specific_start_date.strftime('%Y-%m-%d')} onwards: {specific_count}")



    # Calculate growth between consecutive dates
    df['Growth'] = df['Count'].diff().fillna(0)  # Calculate the difference, filling NaN with 0 for the first row

    # Define significant growth threshold (example: growth > 1)
    threshold = 10
    # Define threshold for displaying dates
    count_threshold = 50

    # Identify significant growth dates
    highlight_df = df[abs(df['Count']) > threshold]
    # Plot the results as a line graph
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Count'], marker='o', linestyle='-', color='b', linewidth=1, markersize=2, label='Members Acquired')
    plt.scatter(highlight_df['Date'], highlight_df['Count'], color='r', zorder=5, label='Significant Growth', s=20, edgecolor='k')

    # Annotate significant growth points with dates
    for _, row in highlight_df.iterrows():
        date = row['Date']
        count = row['Count']
        if count > count_threshold:
            plt.annotate(f"{date.strftime('%Y-%m-%d')}",
                         (date, count),
                         textcoords="offset points",
                         xytext=(0,20),
                         ha='center',
                         fontsize=9,
                         color='red')
        
        plt.annotate(f"{count}",
                     (date, count),
                     textcoords="offset points",
                     xytext=(0,10),
                     ha='center',
                     fontsize=9,
                     color='red')

    total_members_count = df['Count'].sum()
    print(total_members_count)
    # Add total members count to the plot
    plt.text(df['Date'].max(), df['Count'].max(), f"Total Members: {total_members_count}",
         horizontalalignment='right', verticalalignment='top',
         fontsize=12, color='black', bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    plt.figtext(0.99, 0.01, f"Generated on: {timestamp}", horizontalalignment='right', verticalalignment='bottom', fontsize=10, color='gray')

    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Members', fontsize=12)
    plt.title('Number of Members registered per Date with Significant Growth Highlighted', fontsize=14)
    plt.xticks(rotation=45, ha='right')  # Rotate labels and align to the right
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def read_rooms_list():
    '''
    A function which reads in the list of rooms csv exported through synapse admin panel.
    '''
    import csv

    # Read CSV file into a list of dictionaries
    with open('rooms.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]

    return data

def add_someone_to_sm_group(user):
    rooms = read_rooms_list()
    # Display the list of dictionaries
    for row in rooms:
        if row['name'].startswith('SM'):
            print(row['name'])
            add_user_to_room(user, row['room_id'])



if __name__=="__main__":
    #invite_everyone_to_a_room(os.getenv('ROOM_ID'))
    growth_projection()
    #add_someone_to_sm_group(sys.argv[1])
