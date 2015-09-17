class Domain(object):
    # Domain configuration
    DEFAULT_ENDPOINT = None
    DEFAULT_ITEM_TITLE = None
    DEFAULT_RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
    DEFAULT_ITEM_METHODS = ['GET', 'DELETE', 'PUT', 'PATCH']

    def __init__(self):
        """Create the domain object"""
        self.endpoint = self.__class__.DEFAULT_ENDPOINT
        self.item_title = self.__class__.DEFAULT_ITEM_TITLE
        self.resource_methods = self.__class__.DEFAULT_RESOURCE_METHODS
        self.item_methods = self.__class__.DEFAULT_ITEM_METHODS

    def get_endpoint(self):
        """Get the endpoint of the domain.

        :rtype: str
        """
        return self.endpoint

    def get_config(self):
        """Gets the configuration of the domain.

        :rtype: dict
        :return: An EVE configuration dictionary for the domain.
        """
        config = {}

        # Paths
        if self.item_title is not None:
            config['item_title'] = self.item_title

        # HTTP verbs
        config['item_methods'] = self.item_methods
        config['resource_methods'] = self.resource_methods

        # Add schema
        schema = self.get_schema()
        if schema is not None:
            config['schema'] = schema

        return config

    # def get_schema(self):
    #     """Expendable schema generator for the domain.

    #     :rtype: dict
    #     :return: An EVE compliant schema definition.
    #     """
    #     pass
