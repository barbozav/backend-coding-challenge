# from dynaconf import settings
from flask import jsonify, redirect, render_template, request, url_for

from challenge.application import app, projections, repository, tasks
from challenge.application.forms import TranslationForm
from challenge.domain.model.translation import Translation
from challenge.utils.logging import logger


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Application main route.

    Responding to a GET request, it renders a single-page application
    with a form to input an English text to be translated and a table
    containing a list of previous translations ordered by the length
    or the translated text.

    Responding to a POST request it validates if the form (avoiding a
    blank input), creates a new Translation aggregate with the given
    input and then saves it to the repository to be processesd in the
    background (and re-processed if the application breaks for some
    reason before enqueuing the task).

    Args:
        page (int): There is a limit of translations displayed per page,
            and a page can be selected passing this URL argument.

    """
    form = TranslationForm()

    if form.validate_on_submit():
        # POST handling
        logger.debug(f'processing POST "/"')

        text = form.text.data
        translation = Translation.create(text)

        repository.save(translation)

        tasks.translation_task.send(translation.id)
        tasks.projections_task.send(translation.id)

        return redirect(url_for('index'))

    # GET handling
    logger.debug(f'processing GET "/"')

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


@app.route('/json', methods=['GET'])
def translations():
    """Alternative route to get only tranlation JSON.

    This route is used by the frontend to poll translations from a
    single page and dynamically update the translations table.

    Args:
        page (int): There is a limit of translations displayed per page,
            and a page can be selected passing this URL argument.

    """
    page = request.args.get('page')

    logger.debug(f'processing GET "/json"')

    pagination = projections.get(page)

    translations_json = jsonify([{
        'text':
        translation.text or '',
        'status':
        translation.status or '',
        'translated_text':
        translation.translated_text or ''
    } for translation in pagination.items])

    return translations_json
