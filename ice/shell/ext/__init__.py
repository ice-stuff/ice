"""iCE Shell extensions."""


class ShellExt(object):
    """iCE Shell extension class."""

    def __init__(self, logger, debug=False):
        """
        :param logging.Logger logger:
        :param bool debug: Set to True for debug behaviour.
        """
        self.logger = logger
        self.debug = debug

    def start(self, shell):
        """Starts the shell extension.

        It initializes the extension object and calls the
        shell.add_magic_function to setup the shell hooks.

        :param ice.shell.Shell shell:
        """
        self.shell = shell

    def stop(self):
        """Stops the extension. It cleans up the state of the extension."""
        pass

# Import extensions
from . import registry
from . import ec2
from . import experiment
