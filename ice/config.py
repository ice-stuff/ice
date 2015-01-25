"""Configuration parser and class-wrapper."""
import sys
import os
import re
import ConfigParser


def find_config_files(component=None, component_only=False):
    """Returns the list of file paths.
    :param str component: Set to load a specific component (INI file).
    :rtype: `list`
    :return: `list` of `str`.
    """
    # List paths
    cfg_dir_paths = [
        os.path.join(sys.prefix, 'etc', 'ice'),
        os.path.join(sys.prefix, 'local', 'etc', 'ice'),
        os.path.join('/etc/ice'),
        os.path.expanduser('~/.ice')
    ]
    env_paths_str = os.environ.get('ICE_CONFIG_PATHS')
    if env_paths_str is not None:
        env_paths = env_paths_str.split(':')
        for path in env_paths:
            cfg_dir_paths.append(os.path.abspath(path))

    # Build the list
    ret_val = []
    for cfg_dir_path in cfg_dir_paths:
        if not component_only:
            file_path = os.path.join(cfg_dir_path, 'ice.ini')
            if os.path.isfile(file_path):
                ret_val.append(file_path)

        if component is not None:
            file_path = os.path.join(cfg_dir_path, '%s.ini' % component)
            if os.path.isfile(file_path):
                ret_val.append(file_path)

    return ret_val


def get_configuration(component=None):
    """Returns the `config.Configuration` class instance.
    :param str component: Set to load a specific component (INI file).
    :rtype: `config.Configuration`
    :return: Configuration class instance.
    """
    # Get list of files
    file_paths = find_config_files(component)

    # Initialize the parser
    cfg = ConfigParser.SafeConfigParser()
    for file_path in file_paths:
        cfg.read(file_path)

    return Configuration(cfg)


class Configuration(object):

    """Wrapper around ConfigParser.RawConfigParser class. It adds features:

    ## How it works

    1. Default values in get method and non-required options:
        - `ConfigParser` will throw exceptions when an option is not found.
        - It requires default values to be passed in the constructor of the
            class, while in default values are passed in get* method arguments.
    2. Adds methods get_list and get_dict.
        - Based on regular expressions it adds support for multiple levels
            (dictionaries) and for list of values in configuration files.
        - INI extensions - LISTS:
            ```
            OptionName.0 = <Value 0>
            OptionName.1 = <Value 1>
            ...
            ```
        - INI extensions - DICTIONARIES:
            ```
            OptionName.<FieldName 0> = <Value 0>
            OptionName.<FieldName 1> = <Value 1>
            OptionName.<FieldName 2> = <Value 2>
            ...
            ```
    """

    class Error(Exception):
        pass

    class ValueError(Error):
        pass

    class OptionNotFound(Error):
        pass

    def __init__(self, cfg, interpolations={}):
        assert isinstance(cfg, ConfigParser.RawConfigParser)
        assert isinstance(interpolations, dict)

        self.cfg = cfg
        self.interpolations = {
            'HomePath': os.path.expanduser('~')
        }
        for key, value in interpolations.items():
            self.interpolations[key] = value

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
                val = self.cfg.get(section, option, False, self.interpolations)
            elif type is bool:
                val = self.cfg.getboolean(section, option)
            elif type is int:
                val = self.cfg.getint(section, option)
            elif type is float:
                val = self.cfg.getfloat(section, option)
            else:
                raise Configuration.Error('Invalid type required!')
            return val
        except ConfigParser.NoSectionError:
            if required:
                raise Configuration.OptionNotFound(
                    'Section `%s` not found!' % (section)
                )
            return default_value
        except ConfigParser.NoOptionError:
            if required:
                raise Configuration.OptionNotFound(
                    'Option `%s` in section `%s` not found!'
                    % (option, section)
                )
            return default_value
        except ConfigParser.Error as ex:
            raise Configuration.ValueError(
                'Error in reading option %s from section %s: %s'
                % (option, section, str(ex))
            )

    def get_str(self, section, option, default_value=None, required=False):
        """Gets string configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param str default_value: The value to apply if the option is not found.
        :param bool required: Raise a `Configuration.OptionNotFound` exception
            if not found.
        :raises: ice.config.Configuration.OptionNotFound
        :rtype: str
        """
        return self.get_var(section, option, default_value, required, type=str)

    def get_int(self, section, option, default_value=None, required=False):
        """Gets integer configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param int default_value: The value to apply if the option is not found.
        :param bool required: Raise a `Configuration.OptionNotFound` exception
            if not found.
        :raises: ice.config.Configuration.OptionNotFound
        :rtype: int
        """
        return self.get_var(section, option, default_value, required, type=int)

    def get_float(self, section, option, default_value=None, required=False):
        """Gets floating point number, configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param float default_value: The value to apply if the option is not
            found.
        :param bool required: Raise a `Configuration.OptionNotFound` exception
            if not found.
        :raises: ice.config.Configuration.OptionNotFound
        :rtype: float
        """
        return self.get_var(
            section, option, default_value, required, type=float
        )

    def get_bool(self, section, option, default_value=None, required=False):
        """Gets boolean configuration parameter.
        :param str section: The configuration section.
        :param str option: The configuration option name.
        :param bool default_value: The value to apply if the option is not
            found.
        :param bool required: Raise a `Configuration.OptionNotFound` exception
            if not found.
        :raises: ice.config.Configuration.OptionNotFound
        :rtype: bool
        """
        return self.get_var(section, option, default_value, required,
                            type=bool)

    def get_list(self, section, reg_ex):
        """Retrieves a list of values that are in a given section, under option
            keys that match provided regular expression.
        :param str section: The section to look at.
        :param str reg_ex: Regular expression to apply.
        :rtype: list
        :return: List of values.
        """
        reg_ex = reg_ex.lower()  # implementation detail of ConfigParse, all
        # options are converted to lower case
        options = self.cfg.options(section)
        _list = []
        for o in options:
            m = re.match(reg_ex, o)
            if m is None:
                continue
            _list.append(self.cfg.get(section, o))
        return _list

    def get_dict(self, section, reg_ex=r'^(.*)$', group=1):
        """Gets a dictionary with all the options of a given sections, that
            match provided regular expression.
        :param str section: The section to examine.
        :param str reg_ex: Regular expression to apply. Optional, default:
            matches all.
        :param int group: Which matched group of the option name to use as key
            in the dictionary. Optional, default: 1.
        :rtype: dict
        :return: A dictionary with all the matched options.
        """
        reg_ex = reg_ex.lower()  # implementation detail of ConfigParse, all
        # options are converted to lower case
        options = self.cfg.options(section)
        _dict = {}
        for o in options:
            m = re.match(reg_ex, o)
            if m is None:
                continue
            key = m.group(group)
            val = self.cfg.get(section, o)
            _dict[key] = val
        return _dict
