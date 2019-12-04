from __future__ import print_function
import csv
import pickle
import os.path
from datetime import datetime  
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def createtask(startdate, frequency, goaldata):

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
    desc = goaldata["desc"]

    task = {
            'title': name,
            'notes': desc
            }
    service.tasks().insert(tasklist='@default', body=task).execute()

    # make subtasks from csv
    with open('csvfiles/%s.csv' % (goaldata["name"])) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            # Call the Tasks API
            task = {
            'title': name + ': ' + row[0],
            'notes': row[1],
            'due': '%sT12:00:00.000Z' % (startdate),
            'parent': name
            }
            result = service.tasks().insert(tasklist='@default', body=task).execute()
            print(result['id'])
            startdate += timedelta(days=frequency) 