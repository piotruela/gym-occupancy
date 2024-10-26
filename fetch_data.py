import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import subprocess

URL = "https://castlefitness-malbork.cms.efitness.com.pl/na-terenie-klubu"

def fetch_data():
    cookies = {
        "ASP.NET_SessionId": os.getenv("SESSION_ID"),
        ".ASPXAUTH_Cms": os.getenv("AUTH")
    }
    response = requests.get(URL, cookies=cookies)
    
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the span with id="usersIn" and extract its text
    users_in_text = soup.find(id="usersIn").text.strip()
    target_variable = int(users_in_text)  # Convert to integer if needed   

    # Round the current timestamp to the nearest hour or half-hour
    now = datetime.now()
    minutes = now.minute
    if minutes < 15:
        rounded_time = now.replace(minute=0, second=0, microsecond=0)
    elif minutes < 45:
        rounded_time = now.replace(minute=30, second=0, microsecond=0)
    else:
        rounded_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0) 
    
    # Log data with timestamp
    data = {"timestamp": rounded_time, "value": target_variable}
    df = pd.DataFrame([data])
    df.to_csv('data.csv', mode='a', header=not pd.io.common.file_exists('data.csv'), index=False)
    
def push_to_github():
    subprocess.run(["git", "add", "data.csv"])
    subprocess.run(["git", "commit", "-m", "Update data.csv"])
    subprocess.run(["git", "push", "origin", "main"])  # Make sure you're on the main branch

if __name__ == "__main__":
    fetch_data()
    push_to_github()
