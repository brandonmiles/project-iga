from flask import Flask, request, render_template, flash, redirect, url_for
import os
import os.path
import format
import glob
from werkzeug.utils import secure_filename
from flask import send_from_directory
from model import RegForm
from flask_bootstrap import Bootstrap
from score_model import ScoreModel
import pandas as pd
from grade import Grade
import mysql.connector

UPLOAD_FOLDER = 'C:\\Users\\Gautam\\Desktop\\freshStart2\\uploads'
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

#model = ScoreModel()
#model.train_and_test('./data/training_set.tsv')
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
    rubric = {'grammar': form.rubric_range1.data, 'key': form.rubric_range2.data, 'length': form.rubric_range3.data, 'format': form.rubric_range4.data, 'model': form.rubric_range5.data, 'reference': form.rubric_range6.data}
    # How easily or hard it is to lose points from each sections, use None to chose between word count and page count
    weights = {'grammar': form.weights_range1.data, 'allowed_mistakes': form.weights_range2.data, 'key_max': form.weights_range3.data, 'key_min': form.weights_range4.data, 'word_min': form.weights_range5.data, 'word_max': form.weights_range6.data,
           'page_min': form.weights_range7.data, 'page_max': form.weights_range8.data, 'format': form.weights_range9.data, 'reference': form.weights_range10.data}
    # List of allowable fonts
    allowed_fonts = ["Times New Roman", "Calibri Math"]
    # Expected format of the word document, use None to denote a non-graded format criteria
    expected_style = {'font': form.style_range1.data, 'size': form.style_range2.data, 'line_spacing': form.style_range3.data, 'after_spacing': form.style_range4.data,
                      'before_spacing': form.style_range5.data, 'page_width': form.style_range6.data, 'page_height': form.style_range7.data, 'left_margin': form.style_range8.data, 'bottom_margin': form.style_range9.data,
                      'right_margin': form.style_range10.data, 'top_margin': form.style_range11.data, 'header': form.style_range12.data, 'footer': form.style_range13.data, 'gutter': form.style_range14.data, 'indent': form.style_range15.data}
                      
    gradeModel = Grade(rubric, weights, style=expected_style)
    
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
            # add essay to database
    #        command= "INSERT INTO UserEssays (essay, score) VALUES (%s, %s)"
          #  args = (essay, float(form.score.data))
    #        cursor.execute(command, args)
            # write update to database
    #        conn.commit()
            db, gd, out = gradeModel.get_grade(essay)
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
            
            #extension = os.path.splitext(filename)[1]
            
            db, gd, out, essay = gradeModel.get_grade(None, os.path.join(UPLOAD_FOLDER, filename))
            form.grade.data=gd
            form.response.data=out
            form.error.data=db
            form.essay.data = essay
           # return redirect(url_for('uploaded_file',
                                 #filename=filename))
    
                                       
       
    return render_template('registration_custom.html', form=form)


if __name__ == '__main__':
    app.run()
