"""IPython shell wrapper class."""
import IPython
from IPython.config import loader
from IPython.terminal import embed

import ice
from ice import api
from . import ext


class Shell(object):

    """IPython shell wrapper class.

    :type config: ice.config.Configuration
    :type logger: logging.Logger
    """

    def __init__(self, config, logger):
        # Set dependencies
        self.config = config
        self.logger = logger

        # Default banner messages
        self._banner_messages = [
            'Welcome to iCE!',
            'iCE version v{0:s}'.format(ice.__VERSION__),
            'Try help to have a look into the provided commands',
            'You may leave this shell by typing `exit` or pressing Ctrl+D',
            'Try `h <Command>` to get usage information for a given command, or'
            + ' `h` for looking into a brief description of all commands.'
        ]

        # Magic functions
        self._magic_functions = []
        self._magic_functions_dict = {}
        self.add_magic_function('h', self.run_h)
        self.add_magic_function('version', self.run_version)

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

    def start(self, scripts_to_run=None):
        """Starts the shell.

        :param list of [str] scripts_to_run: List of scripts to run.
        :raises Shell.Error: In case of error.
        """
        # Check if inside IPython shell already
        if IPython.get_ipython() is not None:
            raise Shell.Error(
                'Cannot run iCE shell from within an IPython shell!'
            )

        # Make session
        sess = api.session.start()
        if sess is None:
            raise Shell.Error('Failed to start session!')
        self.logger.debug('Session id = {0.id:s}'.format(sess))

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
        api.session.close()

    #
    # Help command
    #

    def run_version(self, magics, args_raw):
        """Prints the version of iCE."""
        print 'iCE version v{0:s}'.format(ice.__VERSION__)

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
