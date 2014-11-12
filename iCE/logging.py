from __future__ import absolute_import
import os
import logging
from logging import config as logging_config

#
# Load configuration
#

etc_path = os.environ.get("ICE_CONFIG_PATH", "/etc/ice")
poss_paths = [
    os.path.join(etc_path, "local.d", "logging.ini"),
    os.path.join(etc_path, "default.d", "logging.ini")
]
for path in poss_paths:
    if os.path.isfile(path):
        logging_config.fileConfig(path, disable_existing_loggers=False)


#
# API
#

def get_logger(name):
    return logging.getLogger(name)


#
# Exports
#

DEBUG = logging.DEBUG
NOTSET = logging.NOTSET
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
FATAL = logging.FATAL
