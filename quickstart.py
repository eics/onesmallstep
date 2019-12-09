from __future__ import print_function
from cs50 import SQL
import pickle
import os.path
from datetime import datetime  
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

db = SQL("sqlite:///goals.db")

def createtask(startdate, frequency, goaldata, steps):

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/tasks']
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('tasks', 'v1', credentials=creds)

    # make parent task with goal name and desc
    name = goaldata["name"].replace('-', ' ')
    desc = goaldata["DESC"]

    task = {
            'title': name,
            'notes': desc
            }
    result = service.tasks().insert(tasklist='@default', body=task).execute()
    parent = result['id']
    previous = None
    # make subtasks
    for row in steps:
        title = name + ': ' + row["step"]
        due = '%sT12:00:00.000Z' % (startdate)
        # Call the Tasks API
        if "description" in row:
            task = {
            'title': title,
            'notes': row["description"],
            'due': due
            }
        else: 
            task = {
            'title': title,
            'due': due
            }
        # create task
        result = service.tasks().insert(tasklist='@default', body=task).execute()
        # add to parent
        service.tasks().move(tasklist='@default', task=result['id'], parent=parent, previous=previous).execute()
        previous = result['id']
        print(result['id'])
        # updates date for next subtask
        startdate = datetime.strptime(startdate, '%Y-%m-%d') + timedelta(days=int(frequency)) 
        startdate = startdate.strftime('%Y-%m-%d')