import ice                          # iCE package
from fabric import api as fab       # Fabric API


@ice.Runner
def run(hosts):
    """A sample iCE runner. It gets the hostnames of all instances and
        prints them out.

    :param dict hosts: Dictionary of ice.entities.Instances objects.
    """
    # Get hostnames of all instances, through fab.execute
    #   First argument: Python function
    #   Second argument: List of hosts
    #   It returns a dictionary with the task result as value.
    hostnames = fab.execute(get_hostname, hosts)

    # Prints
    for key in hostnames:
        print hostnames[key]


@ice.Task
def get_hostname(hosts):
    """A simple iCE task. It returns the FQDN hostname of the remote
        instance.

    :param dict hosts: Dictionary of ice.entities.Instances objects.
    :rtype: str
    :return: The FQDN hostname.
    """
    # Get the FQDN hostname from each node
    hostname = fab.run('hostname -f')
    return hostname
