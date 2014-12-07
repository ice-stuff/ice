"""EC2-like cloud related helper commands."""
import base64

from ice import logging
from ice import ec2_client
from ice import config
from . import session


#
# Globals
#

_logger = logging.get_logger('ice.API.EC2')
_config = config.get_configuration()
_ec2_client = ec2_client.EC2Client(_config, _logger)

#
# API methods
#

def create(amt, ami_id=None, flavor=None, cloud_id=None, sess=None):
    """Creates a list of VMs.

    :param int amt: The number of VMs to create.
    :param str ami_id: The AMI Id to use.
    :param str flavor: The instances flavor (instance type).
    :param str cloud_id: The id of the cloud to use.
    :param ice.entities.Session sess: Active iCE session.
    :rtype: boto.ec2.instance.Reservation
    :return: The reservation.
    """
    global _ec2_client
    user_data = _compile_user_data(sess)
    return _ec2_client.create(amt, user_data, ami_id, flavor, cloud_id)


def wait(timeout=120, cloud_id=None):
    """Wait for instances of current session to come up.

    :param int timeout: The number of seconds to wait before returning `False`.
    :param str cloud_id: The id of the cloud to use.
    :rtype: bool
    :return: `False` if timeout was exceeded. `True` if everything went well.
    """
    global _ec2_client
    return _ec2_client.wait(timeout, cloud_id)


def destroy(instance_ids=None, cloud_id=None):
    """Wait for instances of current session to come up.

    :param list of [str] instance_ids: List of instances to destroy. If not
        provided, all the instances in given cloud and session will be
        destroyed.
    :param str cloud_id: The id of the cloud to use.
    :rtype: list of [boto.ece2.instance.Instance]
    :return: List of destroyed instances (`boto.ece2.instance.Instance`).
    """
    global _ec2_client
    return _ec2_client.destroy(instance_ids, cloud_id)


def get_list(cloud_id=None):
    """Returns list of current reservations.

    :param str cloud_id: The id of the cloud to use.
    :param ice.entities.Session sess: Active iCE session.
    :rtype: list of [boto.ece2.instance.Reservation]
    :return: List of active reservations (`boto.ece2.instance.Reservation`).
    """
    global _ec2_client
    return _ec2_client.get_list(cloud_id)


#
# Helpers
#

def _compile_user_data(sess=None):
    global _config

    # Get session id
    if sess is None:
        sess = session.get_current_session()
        if sess is None:
            return None
    session_id = sess.id

    # Compile user data
    user_data = """#!/bin/bash

curl https://raw.githubusercontent.com/glestaris/iCE/master/agent/ice-register-self.py -O ./ice-register-self.py
chmod +x ./ice-register-self.py
./ice-register-self.py -a http://{0:s}:{1:d} -s {2:s}

""".format(
        _config.get_str('api_client', 'host', 'localhost'),
        _config.get_int('api_client', 'port', 5000),
        session_id
    )

    # Encode and return
    return base64.b64encode(user_data)
