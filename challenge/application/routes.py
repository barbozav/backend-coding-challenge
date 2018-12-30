# from dynaconf import settings
from flask import redirect, render_template, url_for, request, jsonify

from challenge.application import app, repository, tasks, projections
from challenge.application.forms import TranslationForm
from challenge.domain.model.translation import Translation
from challenge.utils.logging import logger


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TranslationForm()
    if form.validate_on_submit():
        text = form.text.data
        translation = Translation.create(text)
        logger.debug(f"processing POST: '{text}'")

        repository.save(translation)

        tasks.translation_task.send(translation.id)
        tasks.projections_task.send(translation.id)

        return redirect(url_for('index'))

    logger.debug(f"processing GET")

    page = request.args.get('page', 1, type=int)
    translations = projections.paginate(page)
    next_url = url_for('index', page=translations['next_page']) \
        if translations['has_next'] else None
    prev_url = url_for('index', page=translations['prev_page']) \
        if translations['has_prev'] else None
    return render_template(
        'index.html',
        form=form,
        translations=translations['items'],
        next_url=next_url,
        prev_url=prev_url)


@app.route('/translations', methods=['POST'])
def translations():
    data = request.get_json()
    page = data.get('page', 1)
    # per_page = data.get('perPage', settings.TRANSLATIONS_PER_PAGE)

    translations = projections.paginate(page)

    if request.method == 'POST':
        translations_json = jsonify([{
            'text': translation.text or '',
            'status': translation.status or '',
            'translated_text': translation.text or ''
        } for translation in translations['items']])
        return translations_json
    else:
        if translations['has_next']:
            next_url = url_for('translations', page=translations['next_page'])
        if translations['has_prev']:
            prev_url = url_for('translations', page=translations['prev_page'])

        return render_template(
            'translations.html',
            translations=translations['items'],
            next_url=next_url or None,
            prev_url=prev_url or None)
