import os
import logging


def get_dummy_logger(name):
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    if os.environ.get('TEST_ICE_DEBUG', '') == '1':
        logger.setLevel(logging.DEBUG)

    return logger
