class Instance(object):

    #
    # SSH key attribute values
    #

    SSH_KEY_FINGERPRINT_DEFAULT = 1

    #
    # Status attribute values
    #

    STATUS_UNKNOWN = 0
    STATUS_RUNNING = 1
    STATUS_UNREACHABLE = 2
    STATUS_BANNED = 3

    #
    # Constructor
    #

    def __init__(self):
        # Identification
        self.uuid = None  # TODO

        # Networking
        self.public_ip_address = None
        self.private_ip_address = None

        # Cloud info
        self.cloud_endpoint = None
        self.security_group_id = None

        # SSH options
        self.ssh_user = 'root'
        self.ssh_key_fingerprint = Instance.SSH_KEY_FINGERPRINT_DEFAULT

        # Instance status
        self.failed_pings_count = 0
        self.status = Instance.STATUS_UNKNOWN
