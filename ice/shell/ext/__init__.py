"""iCE Shell extensions."""


class ShellExt(object):
    """iCE Shell extension class."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        self.shell = shell

        # Set dependencies
        self.config = shell.get_config()
        self.api_client = shell.api_client
        self.logger = shell.get_logger()

        # Session
        self.current_session = None

    def start(self):
        # Set session
        self.current_session = self.shell.current_session

    def stop(self):
        pass

# Shell extensions
from .api import APIShell
from .ec2 import EC2Shell
from .fabric import FabricShell
