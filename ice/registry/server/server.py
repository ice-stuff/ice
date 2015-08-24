import logging

from flask import request
from eve import Eve

from . import validation, domain, config


class RegistryServer(Eve):
    #
    # CHANGE ME: Extend this list to add domains
    #

    _DOMAINS = [domain.InstancesDomain, domain.SessionsDomain]

    def __init__(self, cfg, logger, *args, **kwargs):
        """Create a registry server instance.

        :param ice.registry.server.config.CfgRegistryServer cfg: The
            cfguration object of the server.
        :param logging.Logger logger: The logger to use for logging.
        """
        self.cfg = cfg

        # Eve settings
        self.apiLogger = logger
        self.settings = {
            'API_VERSION': 'v1',    # Version of the API
            'HATEOAS': False,       # Disable HATEOAS
            'IF_MATCH': False,      # Disable If-Match headers

            # Mongo settings
            'MONGO_HOST': cfg.mongo_config['host'],
            'MONGO_PORT': cfg.mongo_config['port'],
            'MONGO_USERNAME': cfg.mongo_config['username'],
            'MONGO_PASSWORD': cfg.mongo_config['password'],
            'MONGO_DBNAME': cfg.mongo_config['db_name']
        }
        self.settings['DOMAIN'] = {}
        for dom in self._DOMAINS:
            self._apply_domain_settings(dom)

        super(RegistryServer, self).__init__(
            settings=self.settings, validator=validation.MyValidator,
            *args, **kwargs
        )

        # Domain hooks
        for dom in self._DOMAINS:
            self._set_domain_hooks(dom)

        # Other rules
        self.add_url_rule(
            '/v1/my_ip', 'handle_get_my_ip', self.handle_get_my_ip
        )

    def run(self):
        """Run the server."""
        super(RegistryServer, self).run(
            host=self.cfg.host,
            port=self.cfg.port,
            debug=self.cfg.debug
        )

    #
    # Setup: domains
    #

    def _apply_domain_settings(self, domain_cls):
        # Setup the domain settings
        self.settings['DOMAIN'][domain_cls.ENDPOINT] = domain_cls.get_config()

    def _set_domain_hooks(self, domain_cls):
        # Instantiate the domain
        dom = domain_cls()

        # Setup the hooks
        for entry, value in domain_cls.__dict__.items():
            if entry.startswith('on_'):
                self.apiLogger.debug(
                    'Registering hook \'%s\' for resource \'%s\''
                    % (entry, domain_cls.ENDPOINT)
                )
                setattr(
                    self, entry + '_' +
                    domain_cls.ENDPOINT, getattr(dom, entry)
                )

    #
    # /my_ip route
    #

    def handle_get_my_ip(self):
        return request.environ['REMOTE_ADDR']
