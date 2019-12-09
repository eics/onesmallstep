# One Small Step: Documentation

## Introduction
Have a large goal but never get to taking steps to achieve it? We help you achieve them one small step at a time. 
SMART goals help push you further, give you a sense of direction, and help you organize and reach your goals.

SMART goals are:
* **S**pecific (simple, sensible, significant).
* **M**easurable (meaningful, motivating).
* **A**chievable (agreed, attainable).
* **R**elevant (reasonable, realistic and resourced, results-based).
* **T**ime bound (time-based, time limited, time/cost limited, timely, time-sensitive).

Our site helps you make smart goals by allowing you to search or upload your own main goal broken down into smaller subgoals or steps. Then, you can add each steps to your Google tasks on a set frequency from a selected start date so you can commit to taking those steps. You can view these tasks from your <a href="https://calendar.google.com/">Google Calendar</a>, <a href="https://mail.google.com/">Gmail</a>, and the Google Tasks app.

## Getting Started

In terminal: 

Make sure you have the requirements:
```pip install -r requirements.txt```

Set the FLASK_APP environment variable:
```export FLASK_APP=application.py```

Run: 
```flask run```

## Basic Usage
When you open up the web app to the main page, you should be presented with a search bar where you can search for a goal that you would like to pursue. Selecting one of the goals that appears in the search results will take you to a goal page, where you can read the steps and step descriptions that make up the overall goal. You can then set the start date for the goal and your desired step frequency. Once you click "Go!" the web app will add the steps to your Google Tasks under a parent task for the goal, which you can view in Google Calendar, Gmail, or the Google Tasks app. 

(Note: If this is your first time adding a goal, you will have to give the webapp (through Google Tasks API) permissions to access your Google account. Click through all the security risk warnings and it will work. If running locally and you want to add tasks to a different Google account, you must delete token.pickle.)

## Uploading New Goals
If you want to upload a new goal, you can click on the "Upload New Goal" link on the navigation bar. On this page you can upload a goal formatted as a CSV file without a header, with each row as a step. A second column for descriptions of each step is optional. Upon uploading, you must input the goal name, goal description, and goal category. You can also keep the goal private (viewable only to you) if you are signed in.

## Modify Existing Goals
You can modify existing goals to suit your needs by navigating to the desired goal page and clicking the "Download and Modify" button to download the CSV. You can then modify the CSV and reupload it as a new goal on the upload page.

## Sign-in
You can sign in using your Google account by clicking the "Google Sign-In" button at the top right corner. Once signed in, you can sign back out by clicking the "Logout" button. Signing in allows you to keep track of how many goals you have decided to work towards achieving (as a motivator!) as well as upload private goals that only you can view. Uploading goals as private is also a good way to save goals for easy access on the /private page. 