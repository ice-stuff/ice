"""Wrapper class for Fabric-related shell commands."""
from __future__ import absolute_import
import os
import sys
from fabric import api as fabric_api
from fabric import tasks as fabric_tasks


class FabricShell(object):

    """Wrapper class for Fabric-related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        # Set dependencies
        self.config = shell.config
        self.api_client = shell.api_client
        self.logger = shell.logger

        # Experiments
        self._experiments = {}

        # Register self
        shell.add_magic_function(
            'load_exp', self.load_exp, usage='<Experiment file path>'
        )
        shell.add_magic_function(
            'ls_exp', self.ls_exp, usage='<Experiment name>'
        )
        shell.add_magic_function(
            'run',
            self.run,
            usage='<Experiment name> <Task name> [<Task arguments> ...]'
        )

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

        # Check path
        if not os.path.isfile(file_path) or not file_path.endswith('.py'):
            return None

        # Setup Python path
        parent_dir_path = os.path.abspath(os.path.dirname(file_path))
        if parent_dir_path not in sys.path:
            sys.path.append(parent_dir_path)

        # Load the module
        if mod_name in self._experiments:
            mod = reload(self._experiments[mod_name])
        else:
            mod = __import__(mod_name)
        if mod is not None:
            self._experiments[mod_name] = mod

        # Reset python path
        del sys.path[len(sys.path) - 1]  # Hack!

        return mod

    #
    # Commands
    #

    def load_exp(self, magics, args_raw):
        """Loads an experiment to iCE."""
        args = args_raw.split()

        # Check path
        try:
            path = args.pop(0)
        except IndexError:
            self.logger.error('Please specify experiment path!')
            return

        # Load module
        mod = self.load_experiment(path)
        if mod is None:
            self.logger.error('Module `%s` failed to be loaded!' % path)
            return
        self.logger.info('Module `%s` is successfully loaded!' % path)

    def ls_exp(self, magis, args_raw):
        """Lists contents of loaded experiment."""
        args = args_raw.split()

        # Parse and check arguments
        try:
            experiment_name = args.pop(0)
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return

        # Is experiment loaded?
        if experiment_name not in self._experiments:
            self.logger.error(
                'Experiment `%s` is not loaded!' % experiment_name
            )
            return
        mod = self._experiments[experiment_name]

        # List contents
        print 'Tasks of module `%s`:' % experiment_name
        for entry, ob in mod.__dict__.items():
            if type(ob) == fabric_tasks.WrappedCallableTask:
                print '* %s: %s' % (entry, ob.__doc__)

    def run(self, magics, args_raw):
        """Runs a task"""
        args = args_raw.split()

        # Parse and check arguments
        try:
            experiment_name = args.pop(0)
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return
        try:
            task_name = args.pop(0)
        except IndexError:
            self.logger.error('Please specify task name!')
            return

        # Is experiment loaded?
        if experiment_name not in self._experiments:
            self.logger.error(
                'Experiment `%s` is not loaded!' % experiment_name
            )
            return
        mod = self._experiments[experiment_name]

        # Is task there?
        try:
            task_func = getattr(mod, task_name)
        except AttributeError:
            self.logger.error(
                'Task `%s.%s` is not found!' % (experiment_name, task_name)
            )
            return

        # Fetch hosts
        hosts = {}
        instances = self.api_client.get_instances_list()
        for inst in instances:
            host_string = '%s@%s' % (
                inst.ssh_username, inst.public_reverse_dns)
            hosts[host_string] = inst

        # Execute
        with fabric_api.settings(hosts=hosts.keys()):
            ret_val = fabric_api.execute(task_func, instances, *args)
            import pprint
            pprint.pprint(ret_val)
