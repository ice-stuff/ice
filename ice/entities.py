"""iCE entities."""


#
# Base entity class
#

class Entity(object):
    """Generic entity.

    :ivar str id: The unique entity id.
    :ivar datetime.DateTime created: When the entity was created.
    :ivar datetime.DateTime update: When the entity was last modified.
    :ivar str etag: A unique e-tag, used for version control.
    """

    def __init__(self, **kwargs):
        # MongoDB stuff
        self.id = kwargs.get('_id', None)
        self.created = kwargs.get('_created', None)
        self.updated = kwargs.get('_updated', None)
        # ETag
        self.etag = kwargs.get('_etag', None)

    def to_dict(self):
        """Converts the entity to dictionary.

        :rtype: dict
        :return: A Python dictionary with the attributes of the entity.
        """
        _dict = {}
        for key, value in self.__dict__.items():
            if value is None:
                continue
            if key.startswith('_'):
                continue
            if key in ['id', 'created', 'updated', 'etag']:  # TODO
                continue
            _dict[key] = value
        return _dict


#
# Session class
#

class Session(Entity):
    """Represents an experimentation session.

    :ivar str client_ip_addr: The IP address of the client.
    """

    def __init__(self, **kwargs):
        super(Session, self).__init__(**kwargs)

        # Attributes
        self.client_ip_addr = kwargs['client_ip_addr']


#
# Instance class
#

class Instance(Entity):
    """Represents a cloud instance.

    :ivar str session_id: The id of the session that owns the instance.
    :ivar list networks: List of networks.
    :ivar str public_ip_addr: Public IP address.
    :ivar str public_reverse_dns: Public reverse DNS.
    :ivar str cloud_id: An identifier for the cloud.
    :ivar str vpc_id: Some identifier for the sub-network / security group or
        VPC within the cloud, on which the instance belogs.
    :ivar str ssh_username: SSH username. Optional, default: root.
    :ivar str ssh_authorized_fingerprint: The SSH fingerprint of the authorized
        SSH key.
    :ivar int failed_pings_count: Amount of pings tha failed to the instance.
    :ivar str status: The status of the instance. Takes values from the
        `Instance.STATUS_*` constants.
    """
    #
    # Status attribute values
    #

    STATUS_UNKNOWN = 'unknown'
    STATUS_RUNNING = 'running'
    STATUS_UNREACHABLE = 'unreachable'
    STATUS_BANNED = 'banned'

    #
    # Constructor
    #

    def __init__(self, **kwargs):
        super(Instance, self).__init__(**kwargs)

        # Session
        self.session_id = kwargs['session_id']

        # Networking
        self.networks = []
        for net in kwargs.get('networks', []):
            my_net = {
                'addr': net['addr']
            }
            if 'iface' in net:
                my_net['iface'] = net['iface']
            if 'bcast_addr' in net:
                my_net['bcast_addr'] = net['bcast_addr']
            self.networks.append(my_net)

        # Public network
        self.public_ip_addr = kwargs['public_ip_addr']
        self.public_reverse_dns = kwargs['public_reverse_dns']

        # Cloud info
        self.cloud_id = kwargs.get('cloud_id', None)
        self.vpc_id = kwargs.get('vpc_id', None)

        # SSH options
        self.ssh_username = kwargs.get('ssh_username', 'root')
        self.ssh_authorized_fingerprint = kwargs['ssh_authorized_fingerprint']

        # Instance status
        self.failed_pings_count = 0
        self.status = Instance.STATUS_RUNNING

    #
    # Setters
    #

    def add_network(self, addr, iface=None, bcast_addr=None):
        """Adds network in the instance.

        :param str addr: The address and mask of the network (e.g.:
            192.168.1.112/24).
        :param str iface: The interface of the network (e.g.: eth0).
        :param str bcast_addr: The broadcast address of the network.
        """
        my_net = {
            'addr': addr
        }
        if iface is not None:
            my_net['iface'] = iface
        if bcast_addr is not None:
            my_net['bcast_addr'] = bcast_addr
        self.networks.append(my_net)

    #
    # Host string
    #

    def get_host_string(self):
        """Generates the host string for SSH.
        :rtype: str
        :return: The SSH host string.
        """
        return '{0.ssh_username:s}@{0.public_reverse_dns:s}'.format(self)
