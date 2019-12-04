import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from quickstart import createtask
from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        searchterm = request.form.get("searchterm") # name the search term searchterm!!
        results = db.execute("SELECT * FROM goals WHERE name LIKE '%:searchterm%'", searchterm=searchterm)
        return redirect("/searchresults", results=results)
    else:
        return render_template("index.html")


@app.route("/searchresult", methods=["GET", "POST"]) # need make searchresult.html that loops through the results, makes button for each one that sends out the id for that result
def searchresult(results):
    if request.method == "POST":
        goal_id = request.form.get("goal_id")
        results = db.execute("SELECT * FROM goals WHERE id = :goalid", goalid=goal_id)
        goalname = results[0]["name"]
        return redirect("goals/<goalname>", goalname=goalname, goal_id=goal_id, results=results)
    else: 
        return render_template("searchresult.html", results)


@app.route("goals/<goalname>", methods=["GET", "POST"], goalname=goal)
def goal(goalname, goal_id, results):
    if request.method == "POST":
        # Ensure start date was submitted
        if not request.form.get("startdate"):
            return apology("What are goals without a start date?!", 403)
        startdate = request.form.get("startdate")
        # Ensure frequency was submitted
        elif not request.form.get("frequency"):
            return apology("Commit yourself to a frequency!!", 403)
        frequency = request.form.get("frequency")
        createtask(startdate, frequency, results)
    return render_template("goal.html", results=results)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
