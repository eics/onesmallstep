import csv
import json
import os
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, send_from_directory, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from quickstart import createtask
from user import User
from helpers import apology, allowed_file, login_required


from oauthlib.oauth2 import WebApplicationClient
import requests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "303120742144-oa0smbgd3o6799hgmaa9lhl3q921ga5q.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "dkIpcyh4qvqkHB_mruW-g6Nn")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

db = SQL("sqlite:///goals.db")

app.secret_key = 'manyrandombytes'

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# When displaying goals, in order to replace descriptions with hyperlinks when discovered
@app.template_filter('regex_search')
def regex_search(s, find):
    """A non-optimal implementation of a regex filter"""
    return re.search(find, s).group(0)


@app.route("/", methods=["GET", "POST"])
def index():
    # counts to display as a motivator
    total=db.execute("SELECT SUM(added) FROM goals")[0]['SUM(added)']
    goals=db.execute("SELECT COUNT(*) FROM goals")[0]['COUNT(*)']
    random=db.execute("SELECT goal_id FROM goals WHERE private=0 ORDER BY random() LIMIT 1")[0]['goal_id']
    # search
    if request.method == "POST":
        searchterm = request.form.get("searchterm").replace(" ", "-")
        return redirect("/searchresults/%s" % (searchterm))
    else: 
        # only authenticated users can view the number of goals they added to tasks
        if current_user.is_authenticated:
            downloaded=db.execute("SELECT downloaded FROM user WHERE id=:id", id=current_user.get_id())[0]['downloaded']
            return render_template("index.html", downloaded=downloaded, goals=goals, total=total, rand=random)
        else: 
            return render_template("index.html", total=total, goals=goals, rand=random)


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # hit the URL from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # Verifying the user and getting user data
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Creating a user in the user table in our db
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect("/")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# Upload file
# From https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
UPLOAD_FOLDER = './csvfiles'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# make goal name from form into file name, replace spaces with dashes
@app.route('/upload', methods=['GET', 'POST']) 
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Set goal name to submitted name with dashes replacing spaces
            goal_name = request.form.get("name").replace(" ", "-")
             # Check if private is checked
            if request.form.get("private"):
                private_bool = 1
            else:
                private_bool = 0
            # Insert new goal into SQL database
            db.execute("INSERT INTO goals (name, desc, category_id, private, user_id, time) VALUES (:name, :desc, :category_id, :private, :user_id, CURRENT_TIMESTAMP)",
                        name=goal_name, desc=request.form.get("desc"), category_id=request.form.get("cat_id"),
                        private=private_bool, user_id=current_user.get_id())
            # Get new goal id
            goal_id = db.execute("SELECT goal_id FROM goals ORDER BY goal_id DESC LIMIT 1")[0]['goal_id']
            # Rename file with id
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(goal_id) + ".csv").replace("\\","/"))

            flash('Goal uploaded :)')
            return redirect(request.url)
    else:
        return render_template("upload.html")

# searchresult.html loops through the results, makes link for each one
@app.route("/searchresults/<searchterm>", methods=["GET"]) 
def searchresult(searchterm):
    descterm = searchterm.replace("-"," ")
    # display goals private only to the user if user is logged in
    if current_user.is_authenticated: 
        results = db.execute("SELECT * FROM goals WHERE (name LIKE '%{searchterm}%' OR desc LIKE '%{descterm}%') AND (private = 0 OR user_id = '{id}')".format(searchterm=searchterm, descterm=descterm, id=current_user.get_id()))
    else:
        results = db.execute("SELECT * FROM goals WHERE (name LIKE '%{searchterm}%' OR desc LIKE '%{descterm}%') AND private = 0".format(searchterm=searchterm, descterm=descterm))
    return render_template("searchresult.html", results=results, term=descterm)


# pages for categories
@app.route("/browse/<category_id>", methods=["GET"])
def category(category_id):
    category = db.execute("SELECT name FROM categories WHERE id = :categoryid", categoryid=category_id)[0]["name"]
    count = db.execute("SELECT COUNT(*) FROM goals WHERE category_id = :categoryid AND (private = 0 OR user_id = :id)", categoryid=category_id, id=current_user.get_id())[0]["COUNT(*)"]
    result = db.execute("SELECT * FROM goals WHERE category_id = :categoryid AND (private = 0 OR user_id = :id) ORDER BY added desc", categoryid=category_id, id=current_user.get_id())
    return render_template("category.html", name=category, goaldata=result, count=count)

# browse all goals
@app.route("/browse", methods=["GET"])
def browse():
    count = db.execute("SELECT COUNT(*) FROM goals WHERE private = 0 OR user_id = :id", id=current_user.get_id())[0]["COUNT(*)"]
    result = db.execute("SELECT * FROM goals WHERE private = 0 OR user_id = :id ORDER BY added desc", id=current_user.get_id())
    return render_template("category.html", name="All goals", goaldata=result, count=count)

# view private goals
@app.route("/private", methods=["GET"])
@login_required
def private():
    count = db.execute("SELECT COUNT(*) FROM goals WHERE private = 1 AND user_id = :id", id=current_user.get_id())[0]["COUNT(*)"]
    result = db.execute("SELECT * FROM goals WHERE private = 1 AND user_id = :id", id=current_user.get_id())
    return render_template("category.html", name="My private goals", goaldata=result, count=count)


# goal.html renders goal info from result and steps from csv and has form for adding to tasks
@app.route("/goals/<goal_id>", methods=["GET", "POST"])
def goal(goal_id):
    goalid = int(goal_id)
    # getting goal info
    result = db.execute("SELECT * FROM goals WHERE goal_id = :goalid", goalid=goalid)
    result=result[0]
    name = result["name"].replace("-", " ")
    steps=[]
    # reading csv
    with open('csvfiles/%s.csv' % (str(goal_id)), encoding="utf8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if len(row) != 1:
                steps.append({"step": row[0], "description": row[1]})
            else: 
                steps.append({"step": row[0]})
    if request.method == "POST":
        # Ensure start date was submitted
        if not request.form.get("startdate"):
            return apology("What are goals without a start date?!", 403)
        startdate = request.form.get("startdate")
        # Ensure frequency was submitted
        if not request.form.get("frequency"):
            return apology("Commit yourself to a frequency!!", 403)
        # Update goal downloaded count
        db.execute("UPDATE goals SET added = added +1 WHERE goal_id = :goalid", goalid=goal_id)
        # Add to number of goals added for user
        if current_user.is_authenticated:
            db.execute("UPDATE user SET downloaded = downloaded +1 WHERE id = :id", id=current_user.get_id())
        frequency = request.form.get("frequency")
        # creates task
        createtask(startdate, frequency, result, steps) 
        # notifies when done
        flash('Added to Google Tasks (view in Calendar/Gmail/App)!')
    return render_template("goal.html", name=name, goaldata=result, steps=steps, goal_id=goal_id, user_id=current_user.get_id())


# allows users to download csv
@app.route("/download/<goal_id>")
def download(goal_id):
    # Update goal downloaded count
    db.execute("UPDATE goals SET branched = branched +1 WHERE goal_id = :goalid", goalid=goal_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                     filename='%s.csv' % (goal_id),
                     as_attachment=True)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
