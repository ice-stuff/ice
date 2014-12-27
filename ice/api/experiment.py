"""Experiment methods."""
from ice import logging
from ice import experiment
from ice import api_client
from ice import config
from . import session

#
# Globals
#

_logger = logging.get_logger('ice.api.experiment')
_config = config.get_configuration()
_api_client = api_client.APIClient(
    _config.get_str('api_client', 'host', 'localhost'),
    _config.get_int('api_client', 'port', 5000)
)

#
# API
#

def load(file_path, sess=None):
    """Loads an experiment.

    :param str file_path: File path of the experiment file.
    :param ice.entities.Session sess: The session to use.
    :rtype: ice.experiment.Experiment
    :return: An experiment instance or `None` in case of error.
    """
    global _api_client, _logger

    # Is session defined?
    if sess is None:
        sess = session.get_current_session()
        if sess is None:
            return None

    try:
        # Make the experiment object
        exp = experiment.Experiment(_logger, sess, _api_client, file_path)
        return exp
    except experiment.Experiment.LoadError as err:  # smt. went wrong
        _logger.error(
            'Failed to load file {0:s}: {1:s}'.format(file_path, str(err))
        )
        return None
