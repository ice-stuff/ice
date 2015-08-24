"""Wrapper class for Fabric-related shell commands."""
from __future__ import absolute_import
import os

from . import ShellExt

from ice import experiment


class FabricShell(ShellExt):

    """Wrapper class for Fabric-related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        super(FabricShell, self).__init__(shell)

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
        experiment_name = os.path.basename(path).replace(
            '.py', ''
        )
        if experiment_name in self._experiments:
            exp = self._experiments.get(experiment_name)
            try:
                exp.load()
            except experiment.Experiment.LoadError as err:
                self.logger.error(
                    'Module `{0:s}` failed to be re-loaded: {1:s}'
                    .format(experiment_name, str(err))
                )
            return
        else:
            exp = api.experiment.load(path)
            if exp is None:
                self.logger.error('Module `%s` failed to be loaded!' % path)
                return
            self._experiments[experiment_name] = exp
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
            exp = self._experiments[experiment_name]
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return

        # List tasks and runners
        tasks, runners = exp.get_contents()
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
            exp = self._experiments[experiment_name]
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return

        # Parse and task name
        try:
            func_name = args.pop(0)
        except IndexError:
            func_name = 'run'  # default

        # Run the task
        res = exp.run(func_name, args=args)
        if res is False:
            self.logger.error(
                'Task `%s.%s` failed!' % (experiment_name, func_name)
            )
