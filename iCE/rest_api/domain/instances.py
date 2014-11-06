from . import Domain


class InstancesDomain(Domain):
    #
    # Domain configuration
    #

    ENDPOINT = 'instances'
    ITEM_TITLE = 'instance'
    ITEM_METHODS = ['GET', 'DELETE']

    @classmethod
    def _get_schema(cls):
        return {
            # Networking
            'private_ip_address': {
                'required': True,
                'type': 'ip'
            },

            'public_ip_address': {
                'required': False,
                'type': 'ip'
            },

            # Cloud info
            'cloud_endpoint': {
                'required': False,
                'type': 'url'
            },
            'security_group_id': {
                'required': False,
                'type': 'string'
            },

            # SSH options
            'ssh_user': {
                'required': False,
                'type': 'string'
            },
            'ssh_key_fingerprint': {
                'required': False,
                'type': 'string'
            }
        }
