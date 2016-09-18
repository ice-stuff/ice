import ice                          # iCE package
from fabric import api as fab       # Fabric API


@ice.Runner
def run(instances):
    """A sample iCE runner. It gets the hostnames of all instances and
        prints them out.

    :param instances: List of entities.Instance objects.
    """
    # Get hostnames of all instances, through fab.execute
    #   First argument: Python function
    #   Second argument: List of hosts
    #   It returns a dictionary with the task result as value.
    hostnames = fab.execute(get_hostname, instances)

    # Prints
    for key in hostnames:
        print(hostnames[key])


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
