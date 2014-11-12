import os
import sys
from IPython.config import loader
from IPython.terminal import embed
from ice import config, logging, api_client


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

        # API configuration
        self.api_client = api_client.APIClient(
            hostname=self.cfg.get_var('shell', 'api_host', 'localhost'),
            port=self.cfg.get_int('shell', 'api_port', 5000)
        )

        # Magic functions
        self.magic_functions = {}
        self.add_magic_function('load_exp', self._cmd_load_exp,
                                usage='<Experiment file path>')
        self.add_magic_function('h', self._cmd_h)

        # Logger
        self.logger = logging.get_logger('shell')
        if self.cfg.get_bool('shell', 'debug', False):
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('Setting log level to DEBUG')

        # Experiments
        self.experiments = {}

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
    # Experiment handling
    #

    def load_experiment(self, file_path):
        """
        Loads an experiment module.

        :param str file_path: The path of the experiment file.
        :rtype: module
        :return: The `module` object or `None` in case of error.
        """
        mod_name = os.path.basename(file_path).replace('.py', '')

        # Is loaded already?
        if mod_name in self.experiments:
            return self.experiments[mod_name]

        # Check path
        if not os.path.isfile(file_path) or not file_path.endswith('.py'):
            return None

        # Setup Python path
        parent_dir_path = os.path.abspath(os.path.dirname(file_path))
        if parent_dir_path not in sys.path:
            sys.path.append(parent_dir_path)

        # Load the module
        mod = __import__(mod_name)
        if mod is not None:
            self.experiments[mod_name] = mod

        # Reset python path
        del sys.path[len(sys.path) - 1]  # Hack!

        return mod

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
        self.magic_functions[alias] = {
            'alias': alias,
            'func': func
        }
        if usage is not None:
            self.magic_functions[alias]['usage'] = usage

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
            + '\n'.join(['* %s' % msg for msg in self.msgs]) + '\n'
            + '* ' + str('*' * 68),
            exit_msg='See ya...'
        )
        for key, entry in self.magic_functions.items():
            shell.define_magic(entry['alias'], entry['func'])

        # Run
        shell()

    #
    # Load experiment command
    #

    def _cmd_load_exp(self, magics, path):
        """Loads an experiment to iCE."""
        # Check path
        if len(path) == 0:
            self.logger.error('Please specify experiment path!')
            return

        # Load module
        mod = self.load_experiment(path)
        if mod is None:
            self.logger.error('Module `%s` failed to be loaded!' % path)
            return
        self.logger.info('Module `%s` is successfully loaded!' % path)

    #
    # Help command
    #

    def _cmd_h(self, magics, definition):
        """Shows list of commands."""
        # Definition is defined :)
        if definition != '':
            if definition in self.magic_functions:
                entry = self.magic_functions[definition]
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
                for key, entry in self.magic_functions.items()
            ]
        )
