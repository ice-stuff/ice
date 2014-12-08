"""Simple API for accessing instances."""
import time

from ice import api_client
from ice import config
from ice import logging
from . import session


#
# Globals
#

_logger = logging.get_logger('ice.api.instances')
_config = config.get_configuration()
_api_client = api_client.APIClient(
    _config.get_str('api_client', 'host', 'localhost'),
    _config.get_int('api_client', 'port', 5000)
)

#
# API
#

def get_list(sess=None):
    """Gets the list of instances for given session.

    :param ice.entities.Session sess: The current session.
    :rtype: list of [ice.entities.Instance]
    :return: List of instance.
    """
    global _api_client, _logger

    # Set current session
    if sess is None:
        sess = session.get_current_session()
        if sess is None:
            _logger.error('Failed to get current session!')
            return []

    # Get list of instances
    return _api_client.get_instances_list(sess.id)


def destroy(instance_ids=None, sess=None):
    """Destroy list of instances.

    :param list of [str] instance_ids: List of instance ids to destroy. `None`
        to destroy all instances in the session.
    :param ice.entities.Session sess: The current session.
    :rtype: bool
    :return: `True` on success and `False` otherwise.
    """
    global _api_client, _logger

    # Set current session
    if sess is None:
        sess = session.get_current_session()
        if sess is None:
            _logger.error('Failed to get current session!')
            return False

    # Fetch instance ids, if not set
    if instance_ids is None:
        instances = _api_client.get_instances_list(sess.id)
        instance_ids = []
        for inst in instances:
            instance_ids.append(inst.id)
    _logger.debug(
        'About to delete {0:d} instances.'.format(len(instance_ids))
    )

    # Controlled delete
    for inst_id in instance_ids:
        inst = _api_client.get_instance(inst_id)
        if inst is None or inst.session_id != sess.id:
            _logger.error(
                'Ignoring instance id {0:s}, instance either not found, or in'
                .format(inst_id)
                + ' wrong session'
            )
            continue
        _api_client.delete_instance(inst_id)

    return True


def get(instance_id, sess=None):
    """Gets a single instance.

    :param str instance_id: The id of the instance.
    :param ice.entities.Session sess: The current session.
    :rtype: ice.entities.Instance
    :return: The instance object or `None`.
    """
    global _api_client, _logger

    # Set current session
    if sess is None:
        sess = session.get_current_session()
        if sess is None:
            _logger.error('Failed to get current session!')
            return None

    # Get instance and check session
    inst = _api_client.get_instance(instance_id)
    if inst is None:
        return None

    # Check session
    if inst.session_id != sess.id:
        _logger.error('Instance found, but in wrong session!')
        return None

    return inst


def wait(amt, timeout=120, sess=None):
    """Wait for `amt` number of instances to appear in the pool.

    :param int amt: The expected number of instances.
    :param int timeout: The timeout of the command, in seconds.
    :param ice.entities.Session sess: The current session.
    :rtype: bool
    :return: `True` if the condition is satisfied and `False` on time out or
        error.
    """
    global _api_client, _logger

    # Session
    if sess is None:
        sess = session.get_current_session()
        if sess is None:
            _logger.error('Failed to get current session!')
            return False

    # Check list of instances
    seconds = 0
    while seconds < timeout:
        instances = _api_client.get_instances_list(sess.id)
        if len(instances) < amt:
            seconds += 5
            _logger.debug(
                '{0:d} instances found, sleeping for 5 seconds...'
                .format(len(instances))
            )
            time.sleep(5)
            continue
        return True

    return False
