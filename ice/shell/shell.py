"""IPython shell wrapper class."""
import argparse

import IPython
from IPython.config import loader
from IPython.terminal import embed

from ice import entities
from ice import api_client
from . import ext


class Shell(object):
    """IPython shell wrapper class.

    :type config: ice.config.Configuration
    :type logger: logging.Logger
    :type api_client: ice.api_client.APIClient
    :type current_session: ice.entities.Session
    """

    def __init__(self, config, logger, api_client):
        # Set dependencies
        self.config = config
        self.api_client = api_client
        self.logger = logger

        # Session
        self.current_session = None

        # Default banner messages
        self._banner_messages = [
            'Welcome to iCE!',
            'Try help to have a look into the provided commands',
            'You may leave this shell by typing `exit` or pressing Ctrl+D',
            'Try `h <Command>` to get usage information for a given command, or'
            + ' `h` for looking into a brief description of all commands.'
        ]

        # Magic functions
        self._magic_functions = []
        self._magic_functions_dict = {}
        self.add_magic_function('h', self.run_h)

        # Add shells extensions
        self._extensions = []
        self._extensions.append(ext.FabricShell(self))
        self._extensions.append(ext.APIShell(self))
        self._extensions.append(ext.EC2Shell(self))

    #
    # Setters / getters
    #

    def get_config(self):
        """Gets the configuration object.
        :rtype: ice.config.Configuration
        :return: The configuration object.
        """
        return self.config

    def get_logger(self):
        """Gets the iCE logger.
        :rtype: logging.Logger
        :return: The iCE logger.
        """
        return self.logger

    #
    # Error
    #

    class Error(Exception):
        pass

    #
    # Message handling
    #

    def add_banner_message(self, msg):
        """Adds a message in the shell header.
        :param str msg: The message to add.
        """
        self._banner_messages.append(msg)

    #
    # Magic function handling
    #

    def add_magic_function(self, alias, callback, usage=None):
        """Adds a magic function to the shell.
        :param str alias: The function alias.
        :param function callback: The callback function.
        :param str usage: The usage string.
        """
        mf = {
            'alias': alias,
            'cb': callback
        }
        if usage is not None:
            mf['usage'] = usage
        self._magic_functions.append(mf)
        self._magic_functions_dict[alias] = mf

    def add_magic_function_v2(self, alias, callback, parser=None):
        """Adds a magic function to the shell.
        :param str alias: Alias of the command
        :param function callback: The callback function.
        :param argparse.ArgumentParser parser: The argument parser.
        """
        mf = {
            'alias': alias,
            'cb': callback,
            'parser': parser
        }
        if parser is not None:
            mf['parser'] = parser
        self._magic_functions.append(mf)
        self._magic_functions_dict[alias] = mf

    #
    # Start shell
    #

    def start(self):
        """
        Starts the shell.

        : raises Shell.Error: In case of error.
        """
        # Check if inside IPython shell already
        if IPython.get_ipython() is not None:
            raise Shell.Error(
                'Cannot run iCE shell from within an IPython shell!'
            )

        # Make session
        try:
            ip_addr = self.api_client.get_my_ip()
        except api_client.APIClient.APIException:
            self.logger.error('Failed to contact API!')
            return
        self.current_session = entities.Session(client_ip_addr=ip_addr)
        if self.api_client.submit_session(self.current_session) is None:
            self.logger.error('Failed to submit session!')
            return

        # Shell configuration
        shell_cfg = loader.Config()
        pc = shell_cfg.PromptManager
        pc.in_template = '$> '
        pc.in2_template = '   '
        pc.out_template = ''

        # Make shell
        shell = embed.InteractiveShellEmbed(
            config=shell_cfg,
            banner1='* ' + str('*' * 68) + '\n'
                    + '\n'.join(
                ['* %s' % msg for msg in self._banner_messages]) + '\n'
                    + '* ' + str('*' * 68),
            exit_msg='See ya...'
        )
        for entry in self._magic_functions:
            shell.define_magic(entry['alias'], entry['cb'])

        # Start extensions
        for ext in self._extensions:
            ext.start()

        # Run
        shell()

        # Stop extensions
        for ext in self._extensions:
            ext.stop()

        # Clean session
        self.api_client.delete_session(self.current_session.id)

    #
    # Help command
    #

    def run_h(self, magics, definition):
        """Shows list of commands."""
        # Definition is defined :)
        if definition != '':
            if definition in self._magic_functions_dict:
                entry = self._magic_functions_dict[definition]
                print entry['cb'].__doc__
                if 'parser' in entry:
                    print entry['parser'].format_help()
                elif 'usage' in entry:
                    print 'Usage: %s %s' % (definition, entry['usage'])
            else:
                help(str(definition))
            return

        # General help
        print 'All commands explained:'
        print '\n'.join(
            [
                ' * %s: %s' % (entry['alias'], entry['cb'].__doc__)
                for entry in self._magic_functions
            ]
        )
