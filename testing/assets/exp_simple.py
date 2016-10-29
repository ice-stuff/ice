import ice
from fabric import api as fab


@ice.Task
def get_hostname(instances):
    """A simple iCE task. It returns the FQDN hostname of the remote
        instance.

    :param instances: List of entities.Instance objects.
    :rtype: str
    :return: The FQDN hostname.
    """
    # Get the FQDN hostname from each node
    hostname = fab.run('hostname -f')
    return hostname
