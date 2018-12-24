import logging
import dramatiq
from flask import flash, redirect, render_template, url_for, request

from app import app
from app.forms import TranslationForm

from unbabel.client import Client


@dramatiq.actor
def translate(text):
    c = Client()
    json = c.request_translation(text)
    app.logger.info(json)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TranslationForm()
    if form.validate_on_submit():
        flash(f'Sending {form.text.data} to translation...')
        # TODO: move it to a worker as it take to much time
        translate.send(form.text.data)
        return redirect(url_for('index'))
    return render_template('index.html', form=form, translations=[])
