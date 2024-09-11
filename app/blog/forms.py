from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

class PostForm(Form):
    title = StringField('Title', [DataRequired()], Length(max=255))
    text = TextAreaField('Content', [DataRequired()]) 

class CommentForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField(u'Comment', validators=[DataRequired()])
