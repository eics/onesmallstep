import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from quickstart import createtask
from helpers import apology, login_required, lookup, usd

db = SQL("sqlite:///goals.db")

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
        searchterm = request.form.get("searchterm")
        results = db.execute("SELECT * FROM goals WHERE name LIKE '%:searchterm%'", searchterm=searchterm)
        return redirect("/searchresults", results=results, term=searchterm)
    else:
        return render_template("index.html")

@app.route("/searchresult", methods=["GET", "POST"]) # need make searchresult.html that loops through the results, makes button for each one that sends out the id for that result
def searchresult(results, term):
    if request.method == "POST":
        goal_id = request.form.get("goal_id")
        result = db.execute("SELECT * FROM goals WHERE id = :goalid", goalid=goal_id)
        goalname = result[0]["name"]
        return redirect("goals/%s" % (goalname), goal_id=goal_id, result=result[0])
    else: 
        return render_template("searchresult.html", results, term)


@app.route("/goals/<goalname>", methods=["GET", "POST"]) # make goal.html to render goal info from result and steps from csv
def goal(goalname, goal_id, result):
    if request.method == "POST":
        # Ensure start date was submitted
        if not request.form.get("startdate"):
            return apology("What are goals without a start date?!", 403)
        startdate = request.form.get("startdate")
        # Ensure frequency was submitted
        if not request.form.get("frequency"):
            return apology("Commit yourself to a frequency!!", 403)
        frequency = request.form.get("frequency")
        createtask(startdate, frequency, result) 
    return render_template("goal.html", goaldata=result)


# Upload file
# From https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
UPLOAD_FOLDER = './csvfiles'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST']) # make goal name from form into file name, replace spaces with dashes
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
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\","/"))
            print("2")
            #### Continue database insert
            db.execute("INSERT INTO goals (name, desc, category_id) VALUES (:name, :desc, :category_id)",
                        name=filename, desc=request.form.get("desc"), category_id=request.form.get("cat_id"))
            return apology("Uploaded")
    else:
        return render_template("upload.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
