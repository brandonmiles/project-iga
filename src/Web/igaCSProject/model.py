from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms.fields import TextAreaField
from wtforms.widgets import SubmitInput
from wtforms.fields.html5 import IntegerRangeField
from wtforms.fields.html5 import IntegerField

class RegForm(FlaskForm):
    essay = TextAreaField(u'', [validators.optional(), validators.length(max=200)])
    range1 = IntegerRangeField('Grammar')
    range2 = IntegerRangeField('Spelling')
    range3 = IntegerRangeField('Complexity')
    score = StringField('Score')
    age = IntegerRangeField('Age', default=0)
    response = TextAreaField(u'Feedback', [validators.optional(), validators.length(max=200)])
    submit = SubmitInput('Submit')
  
