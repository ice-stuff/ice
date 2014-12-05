from __future__ import absolute_import
import logging
from logging import config as logging_config

from ice import config


#
# Load configuration
#

file_paths = config.find_config_files('logging', component_only=True)
for file_path in file_paths:
    logging_config.fileConfig(file_path, disable_existing_loggers=False)


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
