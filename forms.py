from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email

class CommentForm(FlaskForm):
    class Meta:
        csrf = False

    comment = TextAreaField('Comment', validators=[Length(min=1)])

    submit = SubmitField('Add Comment')