"""iCE entities."""


#
# Base entity class
#

class Entity(object):
    """Generic entity.

    :type id: str
    :type created: datetime.datetime
    :type update: datetime.datetime
    :type etag: str
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

    :type client_ip_addr: str
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

    :type session_id: str
    :type networks: list
    :type public_ip_addr: str
    :type public_reverse_dns: str
    :type ssh_username: str
    :type ssh_authorized_fingerprint: str
    """

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
        self.public_reverse_dns = kwargs.get('public_reverse_dns', '')

        # SSH options
        self.ssh_port = int(kwargs.get('ssh_port', 22))
        self.ssh_username = kwargs.get('ssh_username', '')
        self.ssh_authorized_fingerprint = kwargs.get(
            'ssh_authorized_fingerprint', ''
        )

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
