# One Small Step Design Document

## Google Sign-In (/login, /login/callback, /logout routes)
We used this guide (https://realpython.com/flask-google-login/), which uses Flask-Login and OAuthLib to log in users to sessions and generate users in our user table based on their Google Sign-In. user.py houses our User class for Flask-Login. Users signed in can keep track of their private goals as well as know how many goals they’ve decided to work towards achieving. 

## Google Tasks Integration
We used the Google Tasks API to generate Google Tasks for goals and their steps at a specified frequency and from a specified start date. We call it to create the parent task (which represents the main goal), create each subtask (which represent the steps), and move each subtask under the parent task in the right order. 

## Goals.db SQL Database
The goals.db database is set up with 3 main tables:
1. Categories: This stores the 8 categories of goals that we defined as well as their corresponding category id, which helps us sort goals by category, for example, when browsing. 
2. Goals: This stores the uploaded goals and all their relevant information: name, description, category, who uploaded it if applicable, whether or not they’re private, and number of adds and branches, with one line for each goal.
3. Users: This stores user information for users that have signed into the web app using Google, which helps us load profile pictures and match private goals for example. 

While we could have also made an actions table to store which user added to tasks/uploaded/saved which goals so users can view their own history, we didn’t feel like it added much to the user experience since users can very easily view all their added goals in Google Tasks; in addition to their completion status! We deemed counts in our tables to be sufficient. 

## Uploading Goals (/upload)
Visiting the upload page allows the user to upload their own goal CSV by clicking the “Choose File” button, along with the rest of the goal information. If a user is logged in, we give them the option to make the goal private, a.k.a only viewable to them. Once the user clicks the submit button, the CSV is uploaded to the web app’s local directory with the inputted goal name as the file name with hyphens replacing spaces. Changing the name in this way allows for standardization of the goal and file name for easy retrieval. The information is also added to the SQL database as a new row in the goals table.

The upload code is adpated from https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/. 

## Browse (/browse, /browse/<category_id>)
On our home page, we allow users to view all goals and browse for goals by category (ordered by popularity). Only users logged-in can view goals private to them. We get the list of goals for these pages with a SQL query, and we display those goals with the relevant links. 

## Search (/searchresults/<searchterm>)
We also allow users to search on our home page. As long as anything in the goal name or description matches, the search results page will list the goal in the page, ordered by popularity, exactly like how goals are displayed in browse. Just like in browse, we implemented a SQL query. 

## Private (/private)
We added this page after user experience testing. We realized it would be nice to have a page dedicated to the goals you uploaded for yourself if you’re logged in, since these goals are personal and may be used often. This page also happens to be a good way for users to save goals for themselves to add to their tasks later. We use a SQL query on goals to get this information, and we match against the user to only display goals private to that user. The display is just like browse. 

## Displaying Goals (/goals/<goal_id>)
On the left side we display each step and its description with the option for users to download the CSV (see Downloading Goals section) to modify. This display is accomplished by querying the database for the goal name corresponding to the goal id, opening the corresponding CSV file and printing each row as a new HTML line. If the goal description contains a link (for example, to a video), we automatically make it a hyperlink with regex. 

On the right side we have a form that allows users to select their start date and frequency. They can choose frequency from our list or type in their own, implemented with a HTML datalist. Once they submit, we add the parent goal and subgoals to their Google Tasks (see Google Tasks Integration section), and notify them with a flash once we’re done. 

We have a check so that contents on this page can only be viewed if the goal is not private or if the user is logged in and the goal is theirs. This is so that other users can’t just type in the goal id of a private goal in the URL. 

## Downloading Goals (/download/<goal_id>)
At the bottom of each goal page, we’ve included a button that, when clicked, uses the id of the current goal page to get the corresponding CSV file (similar to Displaying Goals section) and send it to the user to download. It also increments the downloaded count by one in the database.