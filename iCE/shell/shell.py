from IPython.config.loader import Config
from IPython.terminal.embed import InteractiveShellEmbed
from .. import config, logging


class Shell(object):

    def __init__(self):
        # Set messages
        self.msgs = [
            'Welcome to iCE!',
            'Try help to have a look into the provided commands',
            'You may leave this shell by typing `exit` or pressing Ctrl+D',
            'Try `h <Command>` to get usage information for a given command, or'
            + ' `h` for looking into a brief description of all commands.'
        ]

        # Configuration
        self.cfg = config.Configuration.get_configuration()

        # Magic functions
        self.magic_functions = []

        # Logger
        self.logger = logging.get_logger('shell')
        if self.cfg.get_bool('shell', 'debug', False):
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('Setting log level to DEBUG')

    #
    # Error
    #

    class Error(Exception):
        pass

    #
    # Message handling
    #

    def add_msg(self, msg):
        """
        Adds a message in the shell header.

        :param str msg: The message to add.
        """
        self.msgs.append(msg)

    #
    # Magic function handling
    #

    def add_magic_function(self, alias, func):
        """
        Adds a magic function to the shell.

        :param str alias: The function alias.
        :param function func: The function pointer.
        """
        self.magic_functions.append(
            {
                'alias': alias,
                'function': func
            }
        )

    #
    # Start shell
    #

    def start(self):
        """
        Starts the shell.

        :raises Shell.Error: In case of error.
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
        shell_cfg = Config()
        pc = shell_cfg.PromptManager
        pc.in_template = '$> '
        pc.in2_template = '   '
        pc.out_template = ''

        # Make shell
        shell = InteractiveShellEmbed(
            config=shell_cfg,
            banner1='* ' + str('*' * 68) + '\n'
            + '\n'.join(['* %s' % msg for msg in self.msgs]) + '\n'
            + '* ' + str('*' * 68),
            exit_msg='See ya...'
        )
        for entry in self.magic_functions:
            shell.define_magic(entry['alias'], entry['function'])

        # Run
        shell()
