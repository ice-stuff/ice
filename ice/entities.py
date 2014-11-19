"""Some common iCE entities."""


#
# Base entity class
#

class Entity(object):

    def __init__(self, **kwargs):
        # MongoDB stuff
        self.id = kwargs.get('_id', None)
        self.created = kwargs.get('_created', None)
        self.updated = kwargs.get('_updated', None)
        # ETag
        self.etag = kwargs.get('_etag', None)

    def to_dict(self):
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
# Instance class
#

class Instance(Entity):
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
        return '{0.ssh_username:s}@{0.public_reverse_dns:s}'.format(self)
