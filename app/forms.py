from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class TranslationForm(FlaskForm):
    text = TextAreaField('Text to translate', validators=[DataRequired()])
    submit = SubmitField('Translate')
