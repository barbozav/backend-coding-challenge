from flask import redirect, render_template, url_for

from app import app
from app import services
from app.models.translation import Translation
from app.repositories import translations_repository as repository
from app.resources.forms import TranslationForm


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TranslationForm()
    if form.validate_on_submit():
        text = form.text.data
        translation = Translation.create(text)
        repository.save(translation)
        services.translate.send(text)
        return redirect(url_for('index'))
    return render_template('index.html', form=form, translations=[])
