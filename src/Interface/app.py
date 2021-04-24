# Author:           Gautam Iyer 
# Date:             02/20/2021
# Project:          CS 4485.001 Spring 2021
# Filename:         app.py
# Description:      The start up application file that startsup the IGA Web Appliction based on Flask
#

# All Imports
#-------------

from flask import Flask, request, render_template, flash, redirect, url_for
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
from score_model import ScoreModel, IdeaModel, StyleModel
import pandas as pd
from grade import Grade
import mysql.connector
import ast
import traceback



# Initialize Application from Config File
# ----------------------------------------

app = Flask(__name__, instance_relative_config=True)
try:
    os.makedirs(app.instance_path)
except OSError as e:
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
try:
    conn = mysql.connector.connect(host=app.config['DB_HOST'], user=app.config['DB_USERNAME'], passwd=app.config['DB_PASSWORD'], database=app.config['DB_NAME'])
    cursor = conn.cursor()
except Exception as e:
    print(e)
    print ('Unable to connect to database ' + app.config['DB_NAME'])


command= "INSERT INTO UserEssays (essay, score) VALUES (%s, %s)"
email = ''

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

# Set Values in Config Dictionary
# -------------------------------
app.config.from_mapping(
    UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads'))
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

    
# Preferences and Email
# ---------------------

@app.route('/updatePreference', methods=['GET', 'POST'])
def updatePreference():
   
    global email
    global rubric
    global style
    global weights
    global gradeModel
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
        
        for keys in rubric:
            rubric[keys] = int(rubric[keys])
            
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
        for keys in style:
            if style[keys] == 0 or style[keys] == 0.0:
                style[keys] = None
        
        
        gradeModel = Grade(rubric, weights, style=style)
    return redirect (url_for('igaResponse'))

@app.route('/updateEmail', methods=['POST'])
def updateEmail():
    global rubric
    global style
    global weights
    if request.method == "POST":
       email = request.form.get("email")
    return redirect (url_for('igaResponse'))

# File upload processing
# -----------------------

def allowed_file(filename):
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

# --------------------------------------------------------
# Main Route processing
# Performs functionality for GET and POST
# For POST performs functionality for all Button Presses
# -----------------------------------------------------------
    
@app.route('/', methods=['GET', 'POST'])
def igaResponse():
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
               current_db, current_gd, current_out  = processEvaluateFile(os.path.join('./',(os.path.relpath((os.path.join(app.config['UPLOAD_FOLDER'], filepath))))))
               if current_gd:
                    form.grade.data = current_gd
                    form.response.data = current_db
                    form.error.data, form.information.data = formatError (current_out)
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
            
        # For Save
        # --------
        
        if request.form.get("Save"):
            if form.grade.data:
                lastrow = processSave(form.essay.data, form.grade.data)
                if lastrow:
                   flash("Addded record to database: " + str(lastrow))
                else:
                   flash('Could not add record to database')
            else:
                if form.uploadFile.data:
                   filepath = form.uploadFile.data
                   filepath = filepath.split(':')
                   filepath = filepath[1].lstrip()
                   current_db, current_gd, current_out = processEvaluateFile(os.path.join('./',(os.path.relpath((os.path.join(app.config['UPLOAD_FOLDER'], filepath))))))
                   if current_gd:
                        form.grade.data = current_gd
                        form.response.data = current_db
                        form.error.data, form.information.data = formatError (current_out)
                        lastrow = processSave(form.essay.data, form.grade.data)
                        if lastrow:
                            flash("Addded record to database: " + str(lastrow))
                        else:
                            flash('Could not add record to database')
                   else:
                        flash("Error in evaluating essay")
                   
                elif form.essay.data:
                   current_db, current_gd, current_out = processEvaluateTextEssay(form.essay.data)
                   if current_gd:
                        form.grade.data = current_gd
                        form.response.data = current_db
                        form.error.data, form.information.data = formatError (current_out)
                        lastrow = processSave(form.essay.data, form.grade.data)
                        if lastrow:
                            flash("Addded record to database: " + str(lastrow))
                        else:
                            flash('Could not add record to database')
                   else:
                        flash("Error in evaluating essay")
                else:
                    flash ("Please enter an essay or upload a file")
                
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
           
        # For Email
        # ---------
        if request.form.get("Email"):
            if form.email.data:
                if form.grade.data:
                    processEmail(form.email.data, form.essay.data, form.uploadFile.data, form.grade.data, form.response.data, form.error.data )
                    flash("Email has been sent to: " + form.email.data)
                else:
                    if form.uploadFile.data:
                        filepath = form.uploadFile.data
                        filepath = filepath.split(':')
                        filepath = filepath[1].lstrip()
                        current_db, current_gd, current_out = processEvaluateFile(os.path.join('./',(os.path.relpath((os.path.join(app.config['UPLOAD_FOLDER'], filepath))))))
                        if current_gd:
                            form.grade.data = current_gd
                            form.response.data = current_db
                            form.error.data, form.information.data = formatError (current_out) 
                            retVal = processEmail(form.email.data, form.essay.data, form.uploadFile.data, current_gd, current_db, form.error.data )
                            if retVal:
                               flash("Email has been sent to: " + form.email.data)      
                    elif form.essay.data:
                        current_db, current_gd, current_out = processEvaluateTextEssay(form.essay.data)
                        if current_gd:
                            form.grade.data = current_gd
                            form.response.data = current_db
                            form.error.data, form.information.data = formatError (current_out) 
                            retVal = processEmail(form.email.data, form.essay.data, form.uploadFile.data, current_gd, current_db, form.error.data )
                            if retVal:
                                flash("Email has been sent to: " + form.email.data)
                    else:
                        flash ("Please enter an essay or upload a file")
            else:
                flash("Please enter a valid email addresss")
                    
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

# Get Text from file uploaded to display in Text Area
# ---------------------------------------------------

def getFileText(filepath):
    f = filepath.split('.')
    # File must be a docx or doc
    if f[len(f) - 1] == "docx" or f[len(f) - 1] == "doc":
        try:
            word = format.Format(filepath)
            t = word.get_text()
            return t
        except Exception as e:
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
            print(e)
            return None
    # File must be a txt
    if f[len(f) - 1] == "txt":
        try:
            t = open(str(filepath), 'r').read()
            return t
        except Exception as e:
            print(e)
            return None

# Evaluates File for grading
# ---------------------------    
    
def processEvaluateFile(filepath):
    global gradeModel
    if filepath:
        try:
            db, gd, out = gradeModel.get_grade(filepath)
            return out, gd, db
        except Exception as e:
            print(e)
            return None, None, None
    else:
       return None, None, None

# Evaluates Input Essay for Grading
# ---------------------------------
    
def processEvaluateTextEssay(essay):
    global gradeModel
    if essay:
        try:
            db, gd, out = gradeModel.get_grade(essay)
            return out, gd, db
        except Exception as e:
            print(e)
            return None, None, None
    else:
       return None, None, None


# Splits the error into information and error and formats the error returned after evaluation for display
# -------------------------------------------------------
    
def formatError(error):
    
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
       #information = information + '{:30s} {:s} {:s} {:s})'.format(infoParts[0], " :", infoParts[1], "\n")       
    return error, information

# Saves the Essay in Database
# ----------------------------   
def processSave(essay, grade):
    global conn
    global cursor
    if cursor:
        try:
            args = (essay, float(grade))
            cursor.execute(command, args)
            # write update to database
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print (e)
            return None
    else:
        return None


# Sends Email to given email address
# ----------------------------------

def processEmail(email, essay, uploadFile, grade, response, error):
    if  email:
        if grade:
            try:
                email_user.send_email(email, grade, response.encode('utf-8'))
                return 1
            except Exception as e:
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
