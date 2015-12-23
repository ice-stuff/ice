"""IPython shell wrapper class."""
import IPython
from IPython.config import loader
from IPython.terminal import embed
import ice
from ice import entities


class CfgShell(object):
    def __init__(self, ssh_id_file_path, debug=False):
        """
        :param string ssh_id_file_path: The path to the SSH id file.
        :param bool debug:
        """
        self.ssh_id_file_path = ssh_id_file_path
        self.debug = debug


class Shell(object):
    """IPython shell wrapper class."""

    class Error(Exception):
        pass

    class Command(object):
        def __init__(self, name, cb, parser=None, usage=None):
            self.name = name
            self.cb = cb
            self.parser = parser
            self.usage = usage

        def get_description(self):
            return self.cb.__doc__

        def get_usage(self):
            if self.parser is not None:
                return self.parser.format_help()
            elif self.usage is not None:
                return 'Usage: %s %s' % (self.name, self.usage)
            else:
                return self.get_description()

    class CommandCallbackWrapper(object):
        def __init__(self, command):
            self.command = command

        def __call__(self, args_str):
            cmd = self.command
            if cmd.parser is not None:
                args = cmd.parser.parse_args(args_str.split())
                return cmd.cb(args)
            else:
                args = args_str.split()
                return cmd.cb(*args)

    def __init__(self, cfg, client, logger, extensions=[]):
        """Create a new shell object.

        :param ice.shell.CfgShell cfg: The shell cofiguration.
        :param ice.registry.client.RegistryClient registry: The registry
            client.
        :param logging.Logger logger:
        :param list extensions: A list of `ice.shell.ext.ShellExt` instances.
        """
        self.cfg = cfg
        self.client = client
        self.logger = logger
        self.extensions = extensions
        self.session = None

        # Default banner messages
        self._banner_messages = [
            'Welcome to iCE version v{0:s}!'.format(ice.__version__),
            'You may leave this shell by typing `exit` or pressing Ctrl+D',
            'Type `h <Command>` to get usage information for a given command,',
            'or `h` for looking into a brief description of all commands.'
        ]

        # Magic functions
        self._commands = []
        self._commands_dict = {}
        self.add_command('h', self.run_h)
        self.add_command('version', self.run_version)
        self.add_command('sess_cd', self.run_sess_cd)
        self.add_command(
            'sess_release', self.run_sess_release,
            usage='When called, iCE will destroy the session on exit.'
        )
        self.add_command(
            'sess_retain', self.run_sess_retain,
            usage='When called, iCE will not destroy the session on exit.'
        )

    def get_session(self):
        """Return the current session.

        :rtype: ice.entities.Session
        """
        return self.session

    def add_banner_message(self, msg):
        """Adds a message in the shell header.

        :param str msg: The message to add.
        """
        self._banner_messages.append(msg)

    def add_command(self, name, callback, usage=None, parser=None):
        """Adds a command to the shell.

        :param str name: The function name.
        :param function callback: The callback function.
        :param str usage: The usage string.
        """
        cmd = self.Command(name, callback)
        if parser is not None:
            cmd.parser = parser
        if usage is not None:
            cmd.usage = usage
        self._commands.append(cmd)
        self._commands_dict[name] = cmd

    def run(self, script_path=None):
        """Run the shell.

        :param str script_path: Script to run.
        :raises Shell.Error: In case of error.
        """
        if IPython.get_ipython() is not None:
            raise Shell.Error(
                'Cannot run iCE shell from within an IPython shell!'
            )

        self.session = entities.Session(
            client_ip_addr=self.client.get_my_ip()
        )
        self.client.submit_session(self.session)
        self.logger.info('Session id = {0.id:s}'.format(self.session))
        self.retain_session = False

        shell_cfg = loader.Config()
        pc = shell_cfg.PromptManager
        pc.in_template = '$> '
        pc.in2_template = '   '
        pc.out_template = ''

        for ext in self.extensions:
            ext.start(self)

        shell = embed.InteractiveShellEmbed(
            config=shell_cfg,
            banner1='* ' + str('*' * 68) + '\n'
                    + '\n'.join(
                ['* %s' % msg for msg in self._banner_messages]) + '\n'
            + '* ' + str('*' * 68),
            exit_msg='See ya...'
        )
        for entry in self._commands:
            shell.register_magic_function(
                self.CommandCallbackWrapper(entry),
                magic_name=entry.name
            )

        if script_path is None:
            shell()
        else:
            shell.safe_execfile_ipy(script_path)

        for ext in self.extensions:
            ext.stop()

        if not self.retain_session:
            self.client.delete_session(self.session)
            self.logger.info(
                'Session `%s` was successfully deleted.' % self.session.id
            )
        else:
            self.logger.info(
                'Current session will not be closed, since it is retained!'
            )

    def run_version(self, magics, args_raw):
        """Prints the version of iCE."""
        print 'iCE version v{0:s}'.format(ice.__version__)

    def run_h(self, definition=''):
        """Shows list of commands."""
        # Definition is defined :)
        if definition != '':
            if definition in self._commands_dict:
                entry = self._commands_dict[definition]
                print entry.get_usage()
            else:
                help(str(definition))
            return

        # General help
        print 'All commands explained:'
        print '\n'.join(
            [
                ' * %s: %s' % (e.name, e.get_description())
                for e in self._commands
            ]
        )

    def run_sess_cd(self, session_id):
        """Changes session."""
        new_session = self.client.get_session(session_id)
        if new_session is None:
            raise Shell.Error('Failed to load session!')

        self.session = new_session
        self.logger.info('New session id = {0.id:s}'.format(self.session))

        self.retain_session = True
        self.logger.info(
            'Loaded session is now retained. Closing this shell will not close'
            + ' the session. Please use `sess_release` to delete the session'
            + ' on exit.'
        )

    def run_sess_release(self):
        """When called, iCE will destroy the session on exit."""
        self.retain_session = False

    def run_sess_retain(self):
        """When called, iCE will retain the session on exit."""
        self.retain_session = True
