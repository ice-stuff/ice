"""Class for session related shell commands."""
from . import ShellExt


class SessionShell(ShellExt):
    """Class for session related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        super(SessionShell, self).__init__(shell)
