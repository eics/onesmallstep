from __future__ import print_function
import csv
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
    desc = goaldata["desc"]

    task = {
            'title': name,
            'notes': desc
            }
    service.tasks().insert(tasklist='@default', body=task).execute()

    # make subtasks
    for row in steps:
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

def main(startdate="19-12-03", frequency=2):
    goaldata = db.execute("SELECT * FROM goals WHERE goal_id = 5")[0]
    steps=[]
    with open('csvfiles/Work-Out.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            print(row)
            steps.append({"step": row[0], "description": row[1]})
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

    # make subtasks
    for row in steps:
        title = name + ': '
        due = '%sT12:00:00.000Z' % (startdate)
        # Call the Tasks API
        task = {
        'title': row[0],
        'notes': row[1],
        'due': due,
        'parent': name
        }
        result = service.tasks().insert(tasklist='@default', body=task).execute()
        print(result['id'])
        startdate += timedelta(days=frequency) 

def test():
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

    # Call the Tasks API
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])

    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print(u'{0} ({1})'.format(item['title'], item['id']))

if __name__ == '__main__':
    main()