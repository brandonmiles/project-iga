from flask import Flask, request, render_template, flash, redirect, url_for
import os
import glob
from werkzeug.utils import secure_filename
from flask import send_from_directory
from model import RegForm
from flask_bootstrap import Bootstrap
from score_model import ScoreModel
import pandas as pd
from grade import Grade
import mysql.connector

UPLOAD_FOLDER = 'C:\\Users\\Gautam\\Desktop\\freshhStart\\uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}


# set up information for database connection
host = 'database-1.cluster-cf5kjev2ovc7.us-east-1.rds.amazonaws.com'
user = 'admin'
password = '8m8oqtTn'
db = 'IGA_DB'

# set up connection
#conn = mysql.connector.connect(host=host, user=user, passwd=password, database=db)
#cursor = conn.cursor()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_mapping(
    SECRET_KEY=b'\xd6\x04\xbdj\xfe\xed$c\x1e@\xad\x0f\x13,@G')
Bootstrap(app)
rubric = {'grammar': 20, 'key': 20, 'length': 20, 'format': 20}
# How easily or hard it is to lose points from each sections, use None to chose between word count and page count
weights = {'grammar': 1, 'key': 10, 'key_min': 2, 'word_min': 300, 'word_max': None, 'page_min': None, 'page_max': None,
           'format': 5}
# List of allowable fonts
allowed_fonts = ["Times New Roman", "Calibri Math"]
# Expected format of the word document, use None to denote a non-graded format criteria
expected_style = {'font': allowed_fonts, 'size': 12, 'line_spacing': 2.0, 'after_spacing': 0.0,
                  'before_spacing': 0.0, 'page_width': 8.5, 'page_height': 11, 'left_margin': 1.0, 'bottom_margin': 1.0,
                  'right_margin': 1.0, 'top_margin': 1.0, 'header': None, 'footer': None, 'gutter': 0.0, 'indent': 1.0}
gradeModel = Grade(rubric, weights, expected_format=expected_style)
#model = ScoreModel()
#model.train_and_test('./data/training_set.tsv', 1)
# How many points each graded section is worth, use None to remove from the rubric

app.debug = True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/', methods=['GET', 'POST'])
def registration():
    form = RegForm(request.form)
    
    if request.method == 'POST':
        '''
            essay = form.essay.data
            grammar = form.range1.data
            keywords = form.range2.data
            length = form.range3.data
            print(grammar)
            print (keywords)
            print (length)
            print (essay)
            form.score.data = model.evaluate(essay)
            print (form.score.data)
            # add essay to database
    #        command= "INSERT INTO UserEssays (essay, score) VALUES (%s, %s)"
            args = (essay, float(form.score.data))
    #        cursor.execute(command, args)
            # write update to database
    #        conn.commit()
            db, gd, out = gradeModel.get_grade_raw(essay)
            print(db)
            print(gd)
            print(out)
            form.grade.data=gd
            form.response.data = out
            form.error.data = db
        '''
        
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filename)
            db, gd, out = gradeModel.get_grade_pdf(os.path.join(UPLOAD_FOLDER, filename))
            print(db)
            print(gd)
            print(out)
            form.grade.data=gd
            form.response.data=out
            form.error.data=db
           # return redirect(url_for('uploaded_file',
                                 #filename=filename))
                                       
       
    return render_template('registration_custom.html', form=form)

if __name__ == '__main__':
    app.run()
