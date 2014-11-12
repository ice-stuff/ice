"""IPython shell wrapper class."""
from IPython.config import loader
from IPython.terminal import embed
from ice.shell import fabric, api


class ShellWrapper(object):

    """IPython shell wrapper class."""

    def __init__(self, config, logger, api_client):
        """
        :param ice.config.Configuration config: The configuration object.
        :param logging.Logger logger: The shell logger.
        :param ice.api_client.APIClient api_client: The API client.
        """
        # Set dependencies
        self.config = config
        self.api_client = api_client
        self.logger = logger

        # Default banner messages
        self._banner_messages = [
            'Welcome to iCE!',
            'Try help to have a look into the provided commands',
            'You may leave this shell by typing `exit` or pressing Ctrl+D',
            'Try `h <Command>` to get usage information for a given command, or'
            + ' `h` for looking into a brief description of all commands.'
        ]

        # Magic functions
        self._magic_functions = {}
        self.add_magic_function('h', self._cmd_h)

        # Add sub-shells
        fabric.FabricShell(self)
        api.APIShell(self)

    #
    # Error
    #

    class Error(Exception):
        pass

    #
    # Message handling
    #

    def add_banner_message(self, msg):
        """
        Adds a message in the shell header.

        :param str msg: The message to add.
        """
        self._banner_messages.append(msg)

    #
    # Magic function handling
    #

    def add_magic_function(self, alias, func, usage=None):
        """
        Adds a magic function to the shell.

        :param str alias: The function alias.
        :param function func: The function pointer.
        :param str usage: The usage string.
        """
        self._magic_functions[alias] = {
            'alias': alias,
            'func': func
        }
        if usage is not None:
            self._magic_functions[alias]['usage'] = usage

    #
    # Start shell
    #

    def start(self):
        """
        Starts the shell.

        : raises Shell.Error: In case of error.
        """
        # Check if inside IPython shell already
        try:
            get_ipython
            raise Shell.Error(
                'Cannot run iCE shell from within an IPython shell!'
            )
        except NameError:
            pass

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
            + '\n'.join(['* %s' % msg for msg in self._banner_messages]) + '\n'
            + '* ' + str('*' * 68),
            exit_msg='See ya...'
        )
        for key, entry in self._magic_functions.items():
            shell.define_magic(entry['alias'], entry['func'])

        # Run
        shell()

    #
    # Help command
    #

    def _cmd_h(self, magics, definition):
        """Shows list of commands."""
        # Definition is defined :)
        if definition != '':
            if definition in self._magic_functions:
                entry = self._magic_functions[definition]
                print entry['func'].__doc__
                if 'usage' in entry:
                    print 'Usage: %s %s' % (definition, entry['usage'])
            else:
                help(str(definition))
            return

        # General help
        print 'All commands explained:'
        print '\n'.join(
            [
                ' * %s: %s' % (key, entry['func'].__doc__)
                for key, entry in self._magic_functions.items()
            ]
        )
