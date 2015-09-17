from .domain import Domain


class SessionsDomain(Domain):
    # Domain configuration
    DEFAULT_ENDPOINT = 'sessions'
    DEFAULT_ITEM_TITLE = 'session'
    DEFAULT_ITEM_METHODS = ['GET', 'DELETE']

    def get_schema(self):
        return {
            'client_ip_addr': {
                'required': True,
                'type': 'ip'
            }
        }
