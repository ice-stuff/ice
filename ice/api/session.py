"""Session methods."""
from ice import api_client
from ice import config
from ice import entities
from ice import logging

#
# Globals
#

_logger = logging.get_logger('ice.api.session')
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
    global _api_client, _logger, _current_session

    # Get IP address of the client
    try:
        ip_addr = _api_client.get_my_ip()
    except api_client.APIClient.APIException:
        _logger.error('Failed to contact API!')
        return None

    # Make session
    ret_val = entities.Session(client_ip_addr=ip_addr)

    # Submit the session
    if _api_client.submit_session(ret_val) is None:
        _logger.error('Failed to submit session!')
        return None

    # Register as current session
    _current_session = ret_val

    return ret_val


def load_session(session_id):
    """Loads specific session.

    :param str session_id: The id of the session to load.
    :rtype: ice.entities.Session
    :return: The loaded session, if found, or `None`.
    """
    global _current_session, _api_client, _logger, _session_shared

    # Find the session in the DB
    sess = _api_client.get_session(session_id)
    if sess is None:
        _logger.error('Session {0:s} was not found!'.format(session_id))
        return None

    # Close current session, if there is one.
    close()

    # Set loaded session as current
    _current_session = sess

    return sess


def get_current_session():
    """Gets the current session.

    :rtype: ice.entities.Session
    :return: The current session.
    """
    global _current_session

    # Is current session set?
    if _current_session is None:
        # no, start a new session
        start()
    return _current_session


def close(session=None):
    """Stop the session.

    :param ice.entities.Session session: The session to stop.
    """
    global _api_client

    # Get current session
    if session is None:
        session = get_current_session()
        if session is None:
            return

    # Delete session from server
    #   TODO: If the session is shared between multiple users, it must not be
    #       deleted by the DB. Instead a registration functionality must be
    #       added to keep track of shells that use a session.
    _api_client.delete_session(session.id)
