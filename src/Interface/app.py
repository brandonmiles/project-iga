"""
 Author:           Gautam Iyer 
 Date:             02/20/2021
 Project:          CS 4485.001 Spring 2021
 Filename:         app.py
 Description:      The start up application file that startsup the IGA Web Appliction based on Flask
 
"""

# All Imports
#-------------

from flask import Flask, request, render_template, flash, redirect, url_for
sys.path.insert(0, '../')
import os
import os.path
from werkzeug.utils import secure_filename
from flask import send_from_directory
from formData.IGAFormData import IGAFormData
from flask_bootstrap import Bootstrap
from flask import render_template
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
import json
from pdfminer.high_level import extract_text
import format as format
import email_user as email_user
import email_user_local as email_user_local
from score_model import ScoreModel, IdeaModel, StyleModel
import pandas as pd
from grade import Grade
import mysql.connector
import ast
import traceback
from datetime import datetime
import urllib.parse


# Initialize Application from Config File
# ----------------------------------------

app = Flask(__name__, instance_relative_config=True)
debug = app.config["DEBUG"]
try:
    os.makedirs(app.instance_path)
except OSError as e:
    if debug:
        print(e)
    pass
    
# Global variables
#-----------------
Bootstrap(app)


# Load Environment
# -----------------

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# Define Global Variables
# ------------------------
conn = ''
cursor = ''

# Connect to database with the required host, username, password and name
# ------------------------
try:
    conn = mysql.connector.connect(host=app.config['DB_HOST'], user=app.config['DB_USERNAME'], passwd=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
    cursor = conn.cursor()
except Exception as e:
    if debug:
        print(e)
    print ('Unable to connect to database ' + app.config['DB_NAME'])

command = "INSERT INTO UserFiles (name, data, grade, feedback, error, email, upload_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
email = ''

# Initialize rubric, weights and style dictionaries with default values
# -------------------------------
rubric = {'grammar': 5, 'key': 5, 'length': 5, 'format': 5, 'model': 5, 'reference': 5}
# How easily or hard it is to lose points from each sections, use None to chose between word count and page count
weights = {'grammar': 1, 'allowed_mistakes': 3, 'key_max': 3, 'key_min': 0, 'word_min': 300, 'word_max': 800,
           'page_min': 1, 'page_max': 4, 'format': 5, 'reference': 5}
  # List of allowable fonts
allowed_fonts = ["Times New Roman", "Calibri Math"]
# Expected format of the word document, use None to denote a non-graded format criteria
style = {'font': allowed_fonts, 'size': 12, 'line_spacing': 2.0, 'after_spacing': 0.0,
                      'before_spacing': 0.0, 'page_width': 8.5, 'page_height': 11, 'left_margin': 1.0, 'bottom_margin': 1.0,
                      'right_margin': 1.0, 'top_margin': 1.0, 'header': 0.0, 'footer': 0.0, 'gutter': 0.0, 'indent': 1.0}

gradeModel = Grade(rubric, weights, style=style)
if debug:
    print('Ready!')
    
# Set Values in Config Dictionary
# -------------------------------
app.config.from_mapping(
    UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads'))
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

    


@app.route('/updatePreference', methods=['GET', 'POST'])
def updatePreference():
    """
    Updates the preference categories after the user inputs their preferences
    
    Returns
    -------
    A redirect back to the current webpage
    """
   # Define global variables
    global email
    global rubric
    global style
    global weights
    global gradeModel
    
    # Store the preferences input
    if request.method == "POST":
        rubric['grammar'] = request.form.get("rubric1")
        rubric['key'] = request.form.get("rubric2")
        rubric['length'] = request.form.get("rubric3")
        rubric['format'] = request.form.get("rubric4")
        rubric['model'] = request.form.get("rubric5")
        rubric['reference'] = request.form.get("rubric6")
        weights['grammar'] = request.form.get("weights1")
        weights['allowed_mistakes'] = request.form.get("weights2")
        weights['key_max'] = request.form.get("weights3")
        weights['key_min'] = request.form.get("weights4")
        weights['word_min'] = request.form.get("weights5")
        weights['word_max'] = request.form.get("weights6")
        weights['page_min'] = request.form.get("weights7")
        weights['page_max'] = request.form.get("weights8")
        weights['format'] = request.form.get("weights9")
        weights['reference'] = request.form.get("weights10")
        style['font'] = request.form.get("style1")
        style['size'] = int(request.form.get("style2"))
        style['line_spacing'] = float(request.form.get("style3"))
        style['after_spacing'] = float(request.form.get("style4"))
        style['before_spacing'] = float(request.form.get("style5"))
        style['page_width'] = float(request.form.get("style6"))
        style['page_height'] = int(request.form.get("style7"))
        style['left_margin'] = float(request.form.get("style8"))
        style['bottom_margin'] = float(request.form.get("style9"))
        style['right_margin'] = float(request.form.get("style10"))
        style['top_margin'] = float(request.form.get("style11"))
        style['header'] = float(request.form.get("style12"))
        style['footer'] = float(request.form.get("style13"))
        style['gutter'] = float(request.form.get("style14"))
        style['indent'] = float(request.form.get("style15"))
        
        # Cast all values for rubric to an integer 
        for keys in rubric:
            rubric[keys] = int(rubric[keys])
        
        # Cast all values for weights to an integer and assign None to all values that are 0.
        for keys in weights:
            weights[keys] = int(weights[keys])
            if keys == 'allowed_mistakes':
                if weights[keys] == 0:
                    weights[keys] = None
            if keys == 'word_min':
                if weights[keys] == 0:
                    weights[keys] = None
            if keys == 'word_max':
                if weights[keys] == 0:
                    weights[keys] = None
            if keys == 'page_min':
                if weights[keys] == 0:
                    weights[keys] = None
            if keys == 'page_max':
                if weights[keys] == 0:
                    weights[keys] = None
        
        # Assigns None to any style category that has a value of 0, 0.0 or "None"
        for keys in style:
            if style[keys] == 0 or style[keys] == 0.0 or style[keys] == "None":
                style[keys] = None
                
        # Updates each category with the values input
        gradeModel.update_rubric(rubric)
        gradeModel.update_weights(weights)
        gradeModel.update_style(style)
        
    return redirect (url_for('igaResponse'))



@app.route('/updateEmail', methods=['POST'])
def updateEmail():
    """
    Updates the email after the user inputs their email
    
    Returns
    -------
    A redirect back to the current webpage
    """
    
    global rubric
    global style
    global weights
    if request.method == "POST":
       email = request.form.get("email")
    return redirect (url_for('igaResponse'))



def allowed_file(filename):
   """
       Checks if given file has extension pdf, txt or docx
       
       Returns
       -------
       True if it does, otherwise returns False
   """
   return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# Error Handling
# --------------

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(InternalServerError)
def handle_500(e):
    original = getattr(e, "original_exception", None)

    if original is None:
        # direct 500 error, such as abort(500)
        return render_template("500.html"), 500

    # wrapped unhandled error
    return render_template("500_unhandled.html", e=original), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("500_generic.html", e=e), 500


# route that allows users to view their results
@app.route('/results', methods=['GET', 'POST'])
def results():
    try:
        form = IGAFormData(request.form)
        # get parameters from URL
        user_email = urllib.parse.unquote(request.args.get('email'))
        date = urllib.parse.unquote(request.args.get('date'))
        if debug:
            print(user_email)
            print(date)
        # retrieve the user's most recent essay
        comm = "SELECT name, data, grade, error, feedback FROM UserFiles WHERE email = %s AND upload_date = %s"
        args = (user_email, date)
        cursor.execute(comm, args)
        # only get the most recent one
        result = cursor.fetchall()
        if not result:
            return render_template('no_results.html')
        result = result[0]
        # insert grade, feedback and error values
        form.grade.data = result[2]
        form.response.data = result[4]
        form.error.data = result[3]
        # save file data to temporary file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], result[0])
        file = open(filename, 'wb')
        file.write(result[1])
        file.close()
        # determine type of file
        filetype = filename.split('.')
        # if word document
        if filetype[len(filetype) - 1] == 'docx':
            # get text from file
            f = format.Format(filename)
            form.essay.data = f.get_text()
        # if pdf file
        elif filetype[len(filetype) - 1] == 'pdf':
            # get text from file
            form.essay.data = extract_text(filename)
        # remove temporary file
        os.remove(filename)
        return render_template('results.html', form=form)
    except Exception as e:
        if debug:
            print(e)
        return render_template('no_results.html')
    


@app.route('/', methods=['GET', 'POST'])
def igaResponse():
    """ 
     Performs a specific operation based on what button the user has clicked. For evaluate, it displays the grade 
     feedback, error and evaluation statistics. For Reset, it clears the webpage. For file upload, it displays the
     content of the file on the screen after upload is clicked.

     Returns
     --------
     A redirect back to the current webpage. 
    """
    global rubric
    global style
    global weights
    global gradeModel
    current_db = ''
    current_gd = ''
    current_out = ''
    current_information = ''
    current_text = ''
    if request.method == 'GET':
       form = IGAFormData(request.form)
       form.essay.data = ''
       form.grade.data = ''
       form.response.data = ''
       form.error.data = ''
       form.uploadFile.data = ''
       form.information.data = ''
       form.email.data = ''
       form.rubric.data = 'Rubric: ' + json.dumps(rubric)
       form.weights.data = 'Weights: ' + json.dumps(weights)
       form.style.data = 'Style: ' + json.dumps(style)
    if request.method == 'POST':
        form = IGAFormData(request.form)
        # For evaluate
        # ------------
        if request.form.get("Evaluate"):
            if form.uploadFile.data:
               filepath = form.uploadFile.data
               filepath = filepath.split(':')
               filepath = filepath[1].lstrip()
               if " " in filepath:
                filepath = filepath.replace(" ", "_")
               current_db, current_gd, current_out  = processEvaluateFile(os.path.join('./',(os.path.relpath((os.path.join(app.config['UPLOAD_FOLDER'], filepath))))))
               if current_gd:
                    form.grade.data = current_gd
                    form.response.data = current_db
                    form.error.data, form.information.data = formatError (current_out)
                    # any uploaded file will be saved to database, open file to read its data
                    path = os.path.join('./', (os.path.relpath((os.path.join(app.config['UPLOAD_FOLDER'], filepath)))))
                    now = datetime.now()
                    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                    processSave(filepath, path, current_gd, form.response.data, form.error.data, form.email.data, formatted_date)

                    # after storing file in database, send email
                    if form.email.data:
                        processEmail(form.email.data, formatted_date)
                        flash("Email has been sent to: " + form.email.data)
                        # remove temp file so space is not wasted
                        os.remove(os.path.join('./', (os.path.relpath((os.path.join(app.config['UPLOAD_FOLDER'], filepath))))))
                    else:
                        flash("Please enter a valid email addresss")       
               else:
                    flash("Error in evaluating essay")
            elif form.essay.data:
               current_db, current_gd, current_out = processEvaluateTextEssay(form.essay.data)
               if current_gd:
                    form.grade.data = current_gd
                    form.response.data = current_db
                    form.error.data, form.information.data = formatError (current_out)
               else:
                    flash("Error in evaluating essay")
            else:
                flash ("Please enter an essay or upload a file")
            # any uploaded file will be saved to database, open file to read its data
        
                
        # For reset
        # ----------
        if request.form.get("Reset"):
           form.essay.data = ''
           form.grade.data = ''
           form.response.data = ''
           form.error.data = ''
           form.information.data = ''
           form.uploadFile.data = ''
           form.email.data = ''
           form.rubric.data = 'Rubric: ' + json.dumps(rubric)
           form.weights.data = 'Weights: ' + json.dumps(weights)
           form.style.data = 'Style: ' + json.dumps(style)
           
      
                    
        # For File Upload
        # ----------------
        if request.form.get("upload"):
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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                t = getFileText(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if t:
                   form.essay.data = t
                   form.uploadFile.data = "Uploaded File: " + file.filename
                else:
                   flash("File could not be parsed into Text")
            else:
                flash("File types accepted are .pdf, .docx, .txt")
                return redirect(request.url)
                
    return render_template('igaView.html', form=form)



def getFileText(filepath):
    """
    Returns
    -------
    The text from the file uploaded to the website
    """
    
    f = filepath.split('.')
    # File must be a docx or doc
    if f[len(f) - 1] == "docx" or f[len(f) - 1] == "doc":
        try:
            word = format.Format(filepath)
            t = word.get_text()
            return t
        except Exception as e:
            if debug:
                print (e)
            return None
    # File must be a pdf
    if f[len(f) - 1] == "pdf":
        try:
            t = extract_text(filepath)
            # PDF reader has trouble dealing with large line spacing, so this is an attempt to fix it.
            t = t.replace("\n\n", " ").replace("  ", " ").replace("  ", " ")
            return t
        except Exception as e:
            if debug:
                print(e)
            return None
    # File must be a txt
    if f[len(f) - 1] == "txt":
        try:
            t = open(str(filepath), 'r').read()
            return t
        except Exception as e:
            if debug:
                print(e)
            return None


def processEvaluateFile(filepath):
    """
     Evaluates file for grading
     
     Returns
     -------
     The debug, grade and output for the essay 
    """
    
    global gradeModel
    if filepath:
        try:
            db, gd, out = gradeModel.get_grade(filepath)
            return out, gd, db
        except Exception as e:
            if debug:
                print(e)
            return None, None, None
    else:
       return None, None, None


    
def processEvaluateTextEssay(essay):
    """
     Evaluates input essay for grading
     
     Returns
     -------
     The debug, grade and output for the essay 
    """

    global gradeModel
    if essay:
        try:
            db, gd, out = gradeModel.get_grade(essay)
            return out, gd, db
        except Exception as e:
            if debug:
                print(e)
            return None, None, None
    else:
       return None, None, None



    
def formatError(error):
    """
     Splits the error into information and error and formats the error returned after evaluation for display
     
     Returns
     -------
     The error and evaluation statistics
    """

    
    split = error.splitlines()
    list_of_tuples = ast.literal_eval(split[1])
    errors = ''
    split[0] = "Number of " + split[0]
    
    for i in range(0, len(list_of_tuples)):
        errors =  errors + "Error " + str(i+1) + ": " + str(list_of_tuples[i]) + "\n"
        
    error = split[0] + '\n' + errors
    information = ''
    
    for i in split[2:]:
       infoParts = i.split(":") 
       information = information + i + '\n'    
    return error, information


# Saves the Essay in Database
# ----------------------------   
def processSave(name, path, grade, feedback, error, email, upload_date):
    global conn
    global cursor
    if cursor:
        try:
            file = open(path, 'rb')
            args = (name, file.read(), grade, feedback, error, email, upload_date)
            cursor.execute(command, args)
            # write update to database
            conn.commit()
            file.close()
            return cursor.lastrowid
        except Exception as e:
            if debug:
                print (e)
            return None
    else:
        return None


# Sends Email to given email address
# ----------------------------------

def processEmail(email, date):
    if  email:
        if date:
            try:
                if debug:
                    email_user_local.send_email_local(email, date)
                else:
                    email_user.send_email(email, date)
                return 1
            except Exception as e:
                if debug:
                    print(e)
                flash("Error in sending Email")
                return None
        else:
            flash("Essay has not been evaluated")
            return None
    else:
        flash("Email address has not been set")
        return None


if __name__ == '__main__':
    app.run()
