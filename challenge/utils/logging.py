import logging

from dynaconf import settings

logger = logging.Logger('challenge', level=settings.LOG_LEVEL)
