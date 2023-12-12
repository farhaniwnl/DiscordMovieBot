# packages datetime, timedelta used to pull API data
# package time used for pulling data every minute and timing with 60 minutes
# the process of the code works as described: pull the code every minute (at :00 minute) and store the values from the API every minute for 60 minutes.

import sqlite3
import requests
import time
from datetime import datetime, timedelta

# Function to retrieve data from the API
def get_api_data():
    response = requests.get("https://4feaquhyai.execute-api.us-east-1.amazonaws.com/api/pi")
    if response.status_code == 200:
        data = response.json()
        # Adjust timestamp to the nearest minute
        data['time'] = (datetime.strptime(data['time'], "%Y-%m-%d %H:%M:%S") + timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:00")
        return data
    else:
        return None

# Function to write data to the database
def write_to_db(data):
    conn = sqlite3.connect('pi_data.db')
    c = conn.cursor()
    # Check for duplicate entry
    c.execute("SELECT * FROM pi_data WHERE time = ?", (data['time'],))
    if not c.fetchone():
        c.execute("INSERT INTO pi_data (factor, pi, time) VALUES (?, ?, ?)", (data['factor'], data['pi'], data['time'])) # how the values are pulled
        conn.commit()
    conn.close()

# Setting up the SQLite database
conn = sqlite3.connect('pi_data.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS pi_data
             (factor INTEGER, pi REAL, time TEXT)''')

# Clear the table each time the script runs
c.execute("DELETE FROM pi_data")
conn.commit()

conn.close()

# Run the job every minute for 60 minutes
end_time = datetime.now() + timedelta(hours=1)
while datetime.now() < end_time:
    current_time = datetime.now()
    next_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
    while datetime.now() < next_minute:
        pass  # Active waiting until the start of the next minute
    data = get_api_data()
    if data:
        write_to_db(data)
