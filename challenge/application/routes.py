# from dynaconf import settings
from flask import jsonify, redirect, render_template, request, url_for

from challenge.application import app, projections, repository, tasks
from challenge.application.forms import TranslationForm
from challenge.domain.model.translation import Translation
from challenge.persistence import session_scope
from challenge.utils.logging import logger


@app.route('/', methods=['GET', 'POST'])
def index():
    """This is the application main route.
    """
    form = TranslationForm()
    if form.validate_on_submit():
        text = form.text.data
        translation = Translation.create(text)
        logger.debug(f"processing POST: '{text}'")

        repository.save(translation)

        tasks.translation_task.send(translation.id)
        projections.update(translation.id)

        return redirect(url_for('index'))

    logger.debug(f"processing GET")

    page = request.args.get('page', 1, type=int)
    translations = projections.get(page)
    next_url = url_for('index', page=translations.next_page) \
        if translations.has_next else None
    prev_url = url_for('index', page=translations.prev_page) \
        if translations.has_prev else None
    return render_template(
        'index.html',
        form=form,
        translations=translations.items,
        next_url=next_url,
        prev_url=prev_url)


@app.route('/translations', methods=['POST'])
def translations():
    data = request.get_json()
    page = data.get('page', 1)

    pagination = projections.get(page)

    translations_json = jsonify([{
        'text': translation.text or '',
        'status': translation.status or '',
        'translated_text': translation.text or ''
    } for translation in pagination.items])
    return translations_json
