from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class TranslationForm(FlaskForm):
    text = TextAreaField(
        '',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter here a text to be translated."})
    submit = SubmitField('Translate')
