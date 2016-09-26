from flask import request
from eve import Eve
from . import validation


class RegistryServer(Eve):
    def __init__(self, cfg, domains, logger, *args, **kwargs):
        """Create a registry server instance.

        :param ice.registry.server.config.CfgRegistryServer cfg: The
            cfguration object of the server.
        :param list domains: List of `ice.registry.server.domain.Domain`
            instances.
        :param logging.Logger logger: The logger to use for logging.
        """
        self.cfg = cfg

        # Eve
        settings = {
            'API_VERSION': 'v2',    # Version of the API
            'HATEOAS': False,       # Disable HATEOAS
            'IF_MATCH': False,      # Disable If-Match headers

            # Setup logging
            'LOGGER_NAME': logger.name,

            # Mongo settings
            'MONGO_HOST': cfg.mongo_config['host'],
            'MONGO_PORT': cfg.mongo_config['port'],
            'MONGO_USERNAME': cfg.mongo_config['username'],
            'MONGO_PASSWORD': cfg.mongo_config['password'],
            'MONGO_DBNAME': cfg.mongo_config['db_name']
        }
        settings['DOMAIN'] = {}
        for dom in domains:
            settings['DOMAIN'][dom.get_endpoint()] = dom.get_config()
        super(RegistryServer, self).__init__(
            settings=settings, validator=validation.MyValidator,
            *args, **kwargs
        )

        # Other rules
        self.add_url_rule(
            '/v2/my_ip', 'handle_get_my_ip', self.handle_get_my_ip
        )

    def run(self, *args, **kwargs):
        """Run the server."""
        super(RegistryServer, self).run(
            host=self.cfg.host,
            port=self.cfg.port,
            debug=self.cfg.debug,
            *args, **kwargs
        )

    def handle_get_my_ip(self):
        header = request.headers.get('X-Forwarded-For', None)
        if header is not None:
            ips = header.split(', ')  # Cloud Foundry hack!
            return ips[0]

        return request.environ['REMOTE_ADDR']
