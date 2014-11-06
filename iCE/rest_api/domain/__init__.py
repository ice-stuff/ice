

#
# Abstract domain class
#

class Domain(object):
    #
    # Domain configuration
    #

    ENDPOINT = None
    ITEM_TITLE = None
    RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
    ITEM_METHODS = ['GET', 'DELETE', 'PUT', 'PATCH']

    @classmethod
    def get_config(cls):
        config = {}

        # Paths
        if cls.ITEM_TITLE is not None:
            config['item_title'] = cls.ITEM_TITLE

        # HTTP verbs
        config['item_methods'] = cls.ITEM_METHODS
        config['resource_methods'] = cls.RESOURCE_METHODS

        # Add schema
        schema = cls._get_schema()
        if schema is not None:
            config['schema'] = schema

        return config

    @classmethod
    def _get_schema(cls):
        return None


#
# Import domains
#

from .instances import InstancesDomain
