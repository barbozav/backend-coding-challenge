from flask import redirect, render_template, url_for

from challenge.application import app, repository, tasks
from challenge.application.forms import TranslationForm
from challenge.domain.model.translation import Translation


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TranslationForm()
    if form.validate_on_submit():
        text = form.text.data

        translation = Translation.create(text)
        repository.save(translation)

        tasks.translation_task.send(translation.id)

        return redirect(url_for('index'))

    return render_template('index.html', form=form, translations=[])
