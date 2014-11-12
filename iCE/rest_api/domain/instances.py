from iCE.rest_api.domain import Domain


class InstancesDomain(Domain):
    #
    # Domain configuration
    #

    ENDPOINT = 'instances'
    _ITEM_TITLE = 'instance'
    _ITEM_METHODS = ['GET', 'DELETE']

    @classmethod
    def _get_schema(cls):
        return {
            # Networking
            'networks': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'addr': {
                            'type': 'string',
                            'required': True
                        },
                        'iface': {
                            'type': 'string',
                            'required': False
                        },
                        'bcast_addr': {
                            'type': 'ip',
                            'required': False
                        }
                    }
                },
            },

            # Public networking
            'public_ip_addr': {
                'required': True,
                'type': 'ip'
            },
            'public_reverse_dns': {
                'required': True,
                'type': 'string'
            },

            # Cloud info
            'cloud_id': {
                'required': False,
                'type': 'url'
            },
            'vpc_id': {
                'required': False,
                'type': 'string'
            },

            # SSH options
            'ssh_username': {
                'required': False,
                'type': 'string',
                'default': 'root'
            },
            'ssh_authorized_fingerprint': {
                'required': True,
                'type': 'string'
            },

            # Status
            'status': {
                'required': False,
                'type': 'string',
                'default': 'running'
            },
            'failed_pings_count': {
                'required': False,
                'type': 'integer',
                'default': 0
            }
        }
