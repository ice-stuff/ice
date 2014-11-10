from eve import Eve
from ..config import Configuration
from .. import logging
from .validation import MyValidator
from .domain import InstancesDomain
from flask import request


class API(Eve):
    #
    # CHANGE ME: Extend this list to add domains
    #

    _DOMAINS = [InstancesDomain]

    #
    # Constructor
    #

    def __init__(self, *args, **kwargs):
        # iCE
        self.cfg = Configuration.get_configuration()
        in_debug = self.cfg.get_bool('api', 'debug', False)
        self.apiLogger = logging.get_logger('ice')
        if in_debug:
            self.apiLogger.setLevel(logging.DEBUG)

        # Initialize settings
        self.settings = {
            # Version of the API
            'API_VERSION': 'v1',
            # Disable HATEOAS
            'HATEOAS': False,
            # Debug mode
            'DEBUG': in_debug,
            # Logging
            'LOGGER_NAME': 'ice'
        }

        # Externals
        self._apply_mongodb_settings()

        # Domains
        self.settings['DOMAIN'] = {}
        for dom in self._DOMAINS:
            self._apply_domain_settings(dom)

        # Call parent
        Eve.__init__(
            self, settings=self.settings, validator=MyValidator, *args,
            **kwargs
        )

        # Domain hooks
        for dom in self._DOMAINS:
            self._set_domain_hooks(dom)

        # Other rules
        self.add_url_rule('/my_ip', 'handle_get_my_ip', self.handle_get_my_ip)

    def run(self, host=None, port=None, debug=None, **options):
        """
        Pass our own subclass of :class:`werkzeug.serving.WSGIRequestHandler
        to Flask.

        :param host: the hostname to listen on. Set this to ``'0.0.0.0'`` to
                     have the server available externally as well. Defaults to
                     ``'127.0.0.1'``.
        :param port: the port of the webserver. Defaults to ``5000``.
        :param debug: if given, enable or disable debug mode.
                      See :attr:`debug`.
        :param options: the options to be forwarded to the underlying
                        Werkzeug server.  See
                        :func:`werkzeug.serving.run_simple` for more
                        information.
        """
        if host is None:
            host = self.cfg.get_var('api', 'host', '0.0.0.0')
        if port is None:
            port = self.cfg.get_int('api', 'port', 5000)
        Eve.run(self, host, port, debug, **options)

    #
    # Setup: externals
    #

    def _apply_mongodb_settings(self):
        self.settings['MONGO_HOST'] = self.cfg.get_var(
            'mongodb', 'host', 'localhost'
        )
        self.settings['MONGO_PORT'] = self.cfg.get_int(
            'mongodb', 'port', 27017
        )
        self.settings['MONGO_USERNAME'] = self.cfg.get_var(
            'mongodb', 'username', ''
        )
        self.settings['MONGO_PASSWORD'] = self.cfg.get_var(
            'mongodb', 'password', ''
        )
        self.settings['MONGO_DBNAME'] = self.cfg.get_var(
            'mongodb', 'db_name', 'iCE'
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
