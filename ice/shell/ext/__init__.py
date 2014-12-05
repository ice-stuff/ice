"""iCE Shell extensions."""


class ShellExt(object):
    """iCE Shell extension class."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        self.shell = shell

    def start(self):
        pass

    def stop(self):
        pass

# Shell extensions
from .api import APIShell
from .ec2 import EC2Shell
from .session import SessionShell
from .fabric import FabricShell
