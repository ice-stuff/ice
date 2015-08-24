"""Configuration object factory"""
import ConfigParser

from ice import ec2_client
from ice.registry import client
from ice.registry import server


class ConfigFactory(object):
    """Configuration factory."""

    class Error(Exception):
        pass

    class ValueError(Error):
        pass

    class OptionNotFound(Error):
        pass

    def __init__(self, config_parser):
        """Creates a configuration factory.

        :param ConfigParser.ConfigParser config_parser: The configuration
            parser.
        """
        self.cfg = configuration(config_parser)

    def get_ec2_cloud_ids(self):
        """List of cloud ids, found in configuration.

        :rtype: `list`
        :return: List of strings.
        """
        clouds = self.cfg.get_str('ec2', 'clouds')
        return clouds.split(',')

    def get_ec2_cloud_auth(self, cloud_id=None):
        """Creates an EC2 authentication config object.

        :param str cloud_id: Cloud id.
        :rtype: `ice.ec2_client.CfgEC2CloudAuth`
        :return: Authentication configuration for EC2.
        """
        cloud_section = 'ec2_{}'.format(cloud_id)
        ec2_url = self.cfg.get_str(cloud_section, 'url')
        if not ec2_url:
            ec2_url = self.cfg.get_str(cloud_section, 'region', required=True)

        return ec2_client.CfgEC2CloudAuth(
            ec2_url,
            self.cfg.get_str(cloud_section, 'aws_access_key', required=True),
            self.cfg.get_str(cloud_section, 'aws_secret_key', required=True)
        )

    def get_ec2_vm_spec(self, cloud_id=None):
        """Creates an EC2 VM specification config object.

        :param str cloud_id: Cloud id.
        :rtype: `ice.ec2_client.CfgEC2VMSpec`
        :return: VM specification configuration for EC2.
        """
        default_flavor = self.cfg.get_str('ec2', 'default_flavor', 't2.micro')

        cloud_section = 'ec2_{}'.format(cloud_id)
        ami_id = self.cfg.get_str(cloud_section, 'default_ami_id',
                                  required=True)
        ssh_key_name = self.cfg.get_str(cloud_section, 'ssh_key_name',
                                        required=True)

        return ec2_client.CfgEC2VMSpec(
            ami_id,
            ssh_key_name,
            flavor=self.cfg.get_str(cloud_section, 'default_flavor',
                                    default_flavor),
            security_group_id=self.cfg.get_str(cloud_section,
                                               'security_group_id'),
            subnet_id=self.cfg.get_str(cloud_section, 'subnet_id')
        )

    def get_registry_client(self):
        """Creates a configuration object for registry client.

        :rtype: `ice.registry.config.CfgRegistryClient`
        :return: Configuration object for registry client.
        """
        return client.CfgRegistryClient(
            host=self.cfg.get_str('registry_client', 'host',
                                  default_value='localhost'),
            port=self.cfg.get_int('registry_client', 'port',
                                  default_value=5000)
        )

    def get_registry_server(self):
        """Creates a configuration object for registry server.

        :rtype: `ice.registry.config.CfgRegistryServer`
        :return: Configuration object for registry server.
        """
        return server.CfgRegistryServer(
            debug=self.cfg.get_bool('registry_server', 'debug',
                                    default_value=False),
            host=self.cfg.get_str('registry_server', 'host',
                                  default_value='localhost'),
            port=self.cfg.get_int('registry_server', 'port',
                                  default_value=5000),
            mongo_host=self.cfg.get_str('mongodb', 'host',
                                        default_value='localhost'),
            mongo_port=self.cfg.get_int('mongodb', 'port',
                                        default_value=27017),
            mongo_user=self.cfg.get_str('mongodb', 'username',
                                        default_value=''),
            mongo_pass=self.cfg.get_str('mongodb', 'password',
                                        default_value=''),
            mongo_db=self.cfg.get_str('mongodb', 'db_name', required=True)
        )


class configuration(object):
    """Wrapper around ConfigParser.RawConfigParser class. It adds features:

    ## How it works

    Default values in get method and non-required options:
        - `ConfigParser` will throw exceptions when an option is not found.
        - It requires default values to be passed in the constructor of the
            class, while in default values are passed in get* method arguments.
   """

    def __init__(self, cfg):
        assert isinstance(cfg, ConfigParser.RawConfigParser)
        self.cfg = cfg

    def get_var(self, section, option,
                default_value=None,
                required=False,
                type=str):
        """
        Generic method the fetch an option.

        :param str section: Configuration section.
        :param str option: Option name.
        :param mixed default_value: The default value, if option is not found.
        :param bool required: If set, an exception will be thrown when the
            option is not found.
        :param type type: The desired type. Will be used for casting the
            resulting value.
        :rtype: mixed
        :return: The actual configuration value or the provided `default_value`
            casted to appropriate `type`.
        """
        try:
            if type is str:
                val = self.cfg.get(section, option, False)
            elif type is bool:
                val = self.cfg.getboolean(section, option)
            elif type is int:
                val = self.cfg.getint(section, option)
            return val
        except ConfigParser.NoOptionError:
            if required:
                raise ConfigFactory.OptionNotFound(
                    'Option `%s` in section `%s` not found!'
                    % (option, section)
                )
            return default_value

    def get_str(self, section, option, default_value=None, required=False):
        """Gets string configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param str default_value: The value to apply if the option is not
            found.
        :param bool required: Raise a `ConfigFactory.OptionNotFound` exception
            if not found.
        :raises: ice.api.config.ConfigFactory.OptionNotFound
        :rtype: str
        """
        return self.get_var(section, option, default_value, required, type=str)

    def get_int(self, section, option, default_value=None, required=False):
        """Gets integer configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param int default_value: The value to apply if the option is not
            found.
        :param bool required: Raise a `ConfigFactory.OptionNotFound` exception
            if not found.
        :raises: ice.api.config.ConfigFactory.OptionNotFound
        :rtype: int
        """
        return self.get_var(section, option, default_value, required, type=int)

    def get_bool(self, section, option, default_value=None, required=False):
        """Gets boolean configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param bool default_value: The value to apply if the option is not
            found.
        :param bool required: Raise a `ConfigFactory.OptionNotFound` exception
            if not found.
        :raises: ice.api.config.ConfigFactory.OptionNotFound
        :rtype: bool
        """
        return self.get_var(section, option, default_value, required,
                            type=bool)
