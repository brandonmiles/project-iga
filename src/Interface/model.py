from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators, SelectField
from wtforms.validators import NumberRange
from wtforms import validators
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms.fields import TextAreaField, html5 as h5fields
from wtforms.widgets import SubmitInput, html5 as h5widgets
from wtforms.fields.html5 import IntegerRangeField
from wtforms.fields.html5 import IntegerField, DecimalField

class RegForm(FlaskForm):
    essay = TextAreaField(u'', [validators.optional(), validators.length(max=200)])
    rubric_range1 = h5fields.IntegerField('Grammar', widget=h5widgets.NumberInput(min=1, max=10) , default=5)
    rubric_range2 = h5fields.IntegerField('Key Words',widget=h5widgets.NumberInput(min=1, max=10) , default=5)
    rubric_range3 = IntegerField('Length', widget=h5widgets.NumberInput(min=1, max=10), default=5)
    rubric_range4 = IntegerField('Format', widget=h5widgets.NumberInput(min=1, max=10), default=5)
    rubric_range5 = IntegerField('Model', widget=h5widgets.NumberInput(min=1, max=10), default=5)
    rubric_range6 = IntegerField('Reference', widget=h5widgets.NumberInput(min=1, max=10), default=5)
    weights_range1 = IntegerField('Grammar', default=1)
    weights_range2 = IntegerField('Allowed Mistakes',  default=3)
    weights_range3 = IntegerField('Key Maximum', default=3)
    weights_range4 = IntegerField('Key Minimum', default=0)
    weights_range5 = IntegerField('Word Minimum', default=300)
    weights_range6 = IntegerField('Word Maximum', default=500)
    weights_range7 = IntegerField('Page Minimum', default=1)
    weights_range8 = IntegerField('Page Maximum', default=4)
    weights_range9 = IntegerField('Format', default=5)
    weights_range10 = IntegerField('Reference', default=5)
    style_range1 = SelectField('Font', choices= [(1,"Times New Roman"), (2,"Calibri Math")])
    style_range2 = IntegerField('Size', default=12)
    style_range3 = DecimalField('Line Spacing', default=2.0)
    style_range4 = DecimalField('After Spacing', default=0)
    style_range5 = DecimalField('Before Spacing', default=0)
    style_range6 = DecimalField('Page Width', default=8.5)
    style_range7 = IntegerField('Page Height', default=11)
    style_range8 = DecimalField('Left Margin', default=1.0)
    style_range9 = DecimalField('Bottom Margin', default=1.0)
    style_range10 = DecimalField('Right Margin', default=1.0)
    style_range11 = DecimalField('Top Margin', default=1.0)
    style_range12 = IntegerField('Header', default=0)
    style_range13 = DecimalField('Footer', default=0)
    style_range14 = DecimalField('Gutter', default=0)
    style_range15 = IntegerField('Indent', default=1)
    grade = StringField('Grade')
    age = IntegerRangeField('Age', default=0)
    response = TextAreaField(u'Feedback', [validators.optional(), validators.length(max=500)])
    error = TextAreaField(u'Error', [validators.optional(), validators.length(max=500)])
    submit = SubmitInput('Submit')
  
