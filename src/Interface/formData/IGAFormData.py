from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators, SelectField
from wtforms.validators import NumberRange
from wtforms import validators
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms.fields import TextAreaField, html5 as h5fields
from wtforms.widgets import SubmitInput, html5 as h5widgets
from wtforms.fields.html5 import IntegerRangeField
from wtforms.fields.html5 import IntegerField, DecimalField
from wtforms.fields.html5 import EmailField
class IGAFormData(FlaskForm):
    essay = TextAreaField(u'', [validators.optional(), validators.length(max=200)])
    grade = StringField('Grade', render_kw={'readonly': True})
    response = TextAreaField(u'',  [validators.optional(), validators.length(max=500)], render_kw={'readonly': True})
    error = TextAreaField(u'',  [validators.optional(), validators.length(max=500)], render_kw={'readonly': True},)
    information = TextAreaField(u'',  [validators.optional(), validators.length(max=500)], render_kw={'readonly': True},)
    email = EmailField('Email Address:', [validators.Email()])
    rubric = StringField (u'', render_kw={'readonly': True})
    weights = StringField (u'', render_kw={'readonly': True})
    style = StringField (u'', render_kw={'readonly': True})
    uploadFile = StringField(u'', render_kw={'readonly': True})
  
