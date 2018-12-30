import logging


def create_logger():
    logger = logging.Logger('challenge', level=logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = create_logger()
