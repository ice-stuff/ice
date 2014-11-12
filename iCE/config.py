"""Configuration parser and class-wrapper."""
import os
import re
import ConfigParser


class Configuration(object):

    """
    Wrapper around ConfigParser.RawConfigParser class. It adds features:

        1) Default values in get method and non-required options:
            - *ConfigParser will throw exceptions when an option is not found.
            - It requires default values to be passed in the constructor of
                the class, while in g4.Val default values are passed in get*
                method arguments.
        2) Adds methods get_list and get_dict.
            - Based on regular expressions it adds support for multiple levels
                (dictionaries) and for list of values in configuration files.
            - INI extensions - LISTS:
                OptionName.0 = <Value 0>
                OptionName.1 = <Value 1>
                ...
            - INI extensions - DICTIONARIES:
                OptionName.<FieldName 0> = <Value 0>
                OptionName.<FieldName 1> = <Value 1>
                OptionName.<FieldName 2> = <Value 2>
                ...
    """

    class Error(Exception):
        pass

    class ValueError(Error):
        pass

    class OptionNotFound(Error):
        pass

    @classmethod
    def get_configuration(cls, component=None):
        """
        Returns the `config.Configuration` class instance.

        :param str component: Set to load a specific component (INI file).
        :rtype: `config.Configuration`
        :return: Configuration class instance.
        """
        etc_path = os.environ.get("ICE_CONFIG_PATH", "/etc/ice")
        cfg = ConfigParser.SafeConfigParser()
        cfg.read(os.path.join(etc_path, "default.d", "ice.ini"))
        if component:
            cfg.read(os.path.join(etc_path, "default.d", "%s.ini" % component))
        cfg.read(os.path.join(etc_path, "local.d", "ice.ini"))
        if component:
            cfg.read(os.path.join(etc_path, "local.d", "%s.ini" % component))
        return cls(cfg)

    def __init__(self, cfg, interpolations={}):
        assert isinstance(cfg, ConfigParser.RawConfigParser)
        assert isinstance(interpolations, dict)

        self.cfg = cfg
        self.interpolations = {
            "HomePath": os.path.expanduser("~"),
            "DevSourcePath": os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..")
            )
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
                raise Configuration.Error("Invalid type required!")
            return val
        except ConfigParser.NoSectionError:
            if required:
                raise Configuration.OptionNotFound(
                    "Section '%s' not found!" % (section)
                )
            return default_value
        except ConfigParser.NoOptionError:
            if required:
                raise Configuration.OptionNotFound(
                    "Option '%s' in section '%s' not found!"
                    % (option, section)
                )
            return default_value
        except ConfigParser.Error as ex:
            raise Configuration.ValueError(
                "Error in reading option %s from section %s: %s"
                % (option, section, str(ex))
            )

    def get_int(self, section, option, default_value=None, required=False):
        return self.get_var(section, option, default_value, required, type=int)

    def get_float(self, section, option, default_value=None, required=False):
        return self.get_var(
            section, option, default_value, required, type=float
        )

    def get_bool(self, section, option, default_value=None, required=False):
        return self.get_var(section, option, default_value, required, type=bool)

    def get_list(self, section, reg_ex):
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

    def get_dict(self, section, reg_ex=r"^(.*)$", group=1):
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
