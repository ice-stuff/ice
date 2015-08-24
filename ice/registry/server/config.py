class CfgRegistryServer(object):
    """Registry server configuration"""

    def __init__(self, host, port,
                 mongo_host, mongo_port, mongo_db,
                 mongo_user='', mongo_pass='',
                 debug=False):
        """Create a registry server

        :param bool debug: If enabled the server will printout more verbose
            messages.
        :param str host: The address to bind to.
        :param int port: The port to bind to.
        :param str mongo_host: The address of the MongoDB server.
        :param int mongo_port: The port of the MongoDB server.
        :param str mongo_user: The username to connect to the MongoDB server.
        :param str mongo_pass: The password to connect to the MongoDB server.
        :param str mongo_db: The name of the database to use in the MongoDB
            server.
        """
        self.debug = debug

        self.host = host
        self.port = port

        self.mongo_config = {
            "host": mongo_host,
            "port": mongo_port,
            "username": mongo_user,
            "password": mongo_pass,
            "db_name": mongo_db
        }
