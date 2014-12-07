"""Session methods."""
from ice import api_client
from ice import config
from ice import entities
from ice import logging

#
# Globals
#

_logger = logging.get_logger('ice.API.Session')
_config = config.get_configuration()
_api_client = api_client.APIClient(
    _config.get_str('api_client', 'host', 'localhost'),
    _config.get_int('api_client', 'port', 5000)
)
_current_session = None

#
# API
#

def start():
    """Start a session.

    :rtype: ice.entities.Session
    :return: The new session or `None` in case of error.
    """
    global _api_client, _logger

    # Make session
    try:
        ip_addr = _api_client.get_my_ip()
    except api_client.APIClient.APIException:
        _logger.error('Failed to contact API!')
        return None
    ret_val = entities.Session(client_ip_addr=ip_addr)
    if _api_client.submit_session(ret_val) is None:
        _logger.error('Failed to submit session!')
        return None

    return ret_val


def get_current_session():
    """Gets the current session.

    :rtype: ice.entities.Session
    :return: The current session.
    """
    global _current_session
    if _current_session is None:
        _current_session = start()
    return _current_session


def close(session=None):
    """Stop the session.

    :param ice.entities.Session session: The session to stop.
    """
    global _api_client
    if session is None:
        session = get_current_session()
        if session is None:
            return
    _api_client.delete_session(session.id)
