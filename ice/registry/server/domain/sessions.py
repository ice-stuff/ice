from .domain import Domain


class SessionsDomain(Domain):
    #
    # Domain configuration
    #

    ENDPOINT = 'sessions'
    _ITEM_TITLE = 'session'
    _ITEM_METHODS = ['GET', 'DELETE']

    @classmethod
    def _get_schema(cls):
        return {
            # Attributes
            'client_ip_addr': {
                'required': True,
                'type': 'ip'
            }
        }
