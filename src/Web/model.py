from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms.fields import TextAreaField
from wtforms.widgets import SubmitInput
from wtforms.fields.html5 import IntegerRangeField
from wtforms.fields.html5 import IntegerField

class RegForm(FlaskForm):
    essay = TextAreaField(u'', [validators.optional(), validators.length(max=200)])
    range1 = IntegerField('Grammar')
    range2 = IntegerField('Key Words')
    range3 = IntegerField('Length')
    range4 = IntegerField('Format')
    score = StringField('Score')
    grade = StringField('Grade')
    age = IntegerRangeField('Age', default=0)
    response = TextAreaField(u'Feedback', [validators.optional(), validators.length(max=500)])
    error = TextAreaField(u'Error', [validators.optional(), validators.length(max=500)])
    submit = SubmitInput('Submit')
  
