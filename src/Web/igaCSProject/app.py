#!bin/python
from flask import Flask, request, render_template
from model import RegForm
from flask_bootstrap import Bootstrap
from score_model import ScoreModel
import pandas as pd
import grade

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=b'\xd6\x04\xbdj\xfe\xed$c\x1e@\xad\x0f\x13,@G')
Bootstrap(app)
model = ScoreModel()
model.train_and_test('./data/training_set.tsv')
app.debug = False
@app.route('/', methods=['GET', 'POST'])
def registration():
    form = RegForm(request.form)
    if request.method == 'POST':
        essay = form.essay.data
        print (essay)
        form.score.data = model.evaluate(essay)
        print (form.score.data)
        form.response.data = 'Test response -- Your score from our intelligent grading system is given above'
    return render_template('registration_custom.html', form=form)

if __name__ == '__main__':
    app.run()
