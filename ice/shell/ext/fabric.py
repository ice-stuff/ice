"""Wrapper class for Fabric-related shell commands."""
from __future__ import absolute_import
import os
import sys

from fabric import api as fabric_api

import ice
from . import ShellExt


class FabricShell(ShellExt):
    """Wrapper class for Fabric-related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        super(ShellExt, self).__init__(shell)

        # Set dependencies
        self.config = shell.config
        self.api_client = shell.api_client
        self.logger = shell.logger

        # Experiments
        self._experiments = {}

        # Register self
        shell.add_magic_function(
            'exp_load', self.load_exp, usage='<Experiment file path>'
        )
        shell.add_magic_function(
            'exp_ls', self.ls_exp, usage='<Experiment name>'
        )
        shell.add_magic_function(
            'exp_run',
            self.run,
            usage='<Experiment name> <Task or runner name> [<Arguments> ...]'
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
    # Running
    #

    def run_experiment(self, runner, *args):
        """
        Runs an experiment runner.

        :param ice.Runner runner: The runner.
        :rtype: `mixed`
        :return: The return value of the runner.
        """
        return self._run(runner, *args)

    def run_task(self, task, *args):
        """
        Runs an experiment task.

        :param ice.Task task: The task.
        :rtype: `dict`
        :return: A dictionary where host keys are the keys and task return
            value is the value of each key.
        """
        return self._run(task, *args)

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
            # Is experiment loaded?
            if experiment_name not in self._experiments:
                self.logger.error(
                    'Experiment `%s` is not loaded!' % experiment_name
                )
                return
            mod = self._experiments[experiment_name]
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return

        # Get strings (lines)
        runners = []
        tasks = []
        for entry, ob in mod.__dict__.items():
            # Do we know this function?
            if not isinstance(ob, ice.Callable):
                continue

            # Has help-doc?
            if ob.help_msg is not None:
                line = '* %s: %s' % (entry, ob.help_msg)
            else:
                line = '* %s' % entry

            # Task or runner
            if isinstance(ob, ice.Task):
                tasks.append(line)
            elif isinstance(ob, ice.Runner):
                runners.append(line)

        # List tasks and runners
        print '> Module `%s`:' % experiment_name
        if len(runners) > 0:
            print 'Runners:'
            print '\n'.join(runners)
        if len(tasks) > 0:
            print 'Tasks:'
            print '\n'.join(tasks)

    def run(self, magics, args_raw):
        """Runs a task or an experiment."""
        args = args_raw.split()

        # Parse and check experiment name
        try:
            experiment_name = args.pop(0)
            # Is experiment loaded?
            if experiment_name not in self._experiments:
                self.logger.error(
                    'Experiment `%s` is not loaded!' % experiment_name
                )
                return
            mod = self._experiments[experiment_name]
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return

        # Parse and task name
        try:
            task_name = args.pop(0)
        except IndexError:
            task_name = 'run'  # default
        # Is task there?
        try:
            task_func = getattr(mod, task_name)
            if not isinstance(task_func, ice.Callable):
                self.logger.error(
                    'Attribute `%s.%s` is not a callable!'
                    % (experiment_name, task_name)
                )
                return
        except AttributeError:
            self.logger.error(
                'Callable `%s.%s` is not found!' % (experiment_name, task_name)
            )
            return

        # Execute
        if isinstance(task_func, ice.Task):
            self.run_task(task_func, *args)
        elif isinstance(task_func, ice.Runner):
            self.run_experiment(task_func, *args)

    #
    # Helpers
    #

    def _run(self, func, *args):
        # Fetch hosts
        hosts = {}
        instances = self.api_client.get_instances_list()
        for inst in instances:
            host_string = inst.get_host_string()
            hosts[host_string] = inst

        # Execute
        with fabric_api.settings(hosts=hosts.keys()):
            # Prepare arguments
            args = [hosts] + list(args)
            # Run
            if isinstance(func, ice.Runner):
                return func(*args)
            elif isinstance(func, ice.Task):
                return fabric_api.execute(func, *args)
            else:
                return None
