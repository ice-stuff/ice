class Instance(object):
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
        # Identification
        self.id = None

        # Networking
        self.networks = []
        for net in kwargs.get('networks', []):
            my_net = {
                'addr': net['addr']
            }
            if net.has('iface'):
                my_net['iface'] = net['iface']
            if net.has('bcast_addr'):
                my_net['bcast_addr'] = net['bcast_addr']
            self.networks.append(my_net)

        # Cloud info
        self.cloud_id = kwargs.get('cloud_id', None)
        self.vpc_id = kwargs.get('vpc_id', None)

        # SSH options
        self.ssh_username = kwargs.get('ssh_username', 'root')
        self.ssh_authorized_fingerprint = kwargs['ssh_authorized_fingerprint']

        # Instance status
        self.failed_pings_count = 0
        self.status = Instance.STATUS_RUNNING
