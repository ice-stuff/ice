class Domain(object):
    #
    # Domain configuration
    #

    ENDPOINT = None
    _ITEM_TITLE = None
    _RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
    _ITEM_METHODS = ['GET', 'DELETE', 'PUT', 'PATCH']

    @classmethod
    def get_config(cls):
        """Gets the configuration of the domain.

        :rtype: dict
        :return: An EVE configuration dictionary for the domain.
        """
        config = {}

        # Paths
        if cls._ITEM_TITLE is not None:
            config['item_title'] = cls._ITEM_TITLE

        # HTTP verbs
        config['item_methods'] = cls._ITEM_METHODS
        config['resource_methods'] = cls._RESOURCE_METHODS

        # Add schema
        schema = cls._get_schema()
        if schema is not None:
            config['schema'] = schema

        return config

    @classmethod
    def _get_schema(cls):
        """Expendable schema generator for the domain.

        :rtype: dict
        :return: An EVE compliant schema definition.
        """
        return None
