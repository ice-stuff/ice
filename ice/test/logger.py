import os
import logging


def get_dummy_logger(name):
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    if os.environ.get('TEST_ICE_DEBUG', '') == '1':
        logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s :: %(message)s'
    )
    ch.setFormatter(formatter)

    ch.setLevel(logging.INFO)
    if os.environ.get('TEST_ICE_DEBUG', '') == '1':
        ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)

    return logger
