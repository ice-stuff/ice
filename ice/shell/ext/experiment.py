"""Wrapper class for Fabric-related shell commands."""
import os
from ice import experiment
from . import ShellExt


class ExperimentShell(ShellExt):
    """Wrapper class for Fabric-related shell commands."""

    def __init__(self, registry, ssh_id_file_path, logger, debug=False):
        """
        :param ice.registry.client.RegistryClient registry:
        :param string ssh_id_file_path:
        :param logging.Logger logger:
        :param bool debug: Set to True for debug behaviour.
        """
        self.registry = registry
        self.ssh_id_file_path = ssh_id_file_path
        self._experiments = {}
        super(ExperimentShell, self).__init__(logger, debug)

    def start(self, shell):
        """Starts the shell extension.

        It initializes the extension object and calls the
        shell.add_command to setup the shell hooks.

        :param ice.shell.Shell shell:
        """
        super(ExperimentShell, self).start(shell)

        shell.add_command(
            'exp_load', self.load_exp, usage='<Experiment file path>'
        )
        shell.add_command(
            'exp_ls', self.ls_exp, usage='<Experiment name>'
        )
        shell.add_command(
            'exp_run', self.run_exp,
            usage='<Experiment name> <Task or runner name> [<Arguments> ...]'
        )

    def load_exp(self, *args):
        """Loads an experiment to iCE."""
        args = list(args)

        try:
            path = args.pop(0)
        except IndexError:
            self.logger.error('Please specify experiment path!')
            return

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
            try:
                exp = experiment.Experiment(self.logger, path)
            except experiment.Experiment.LoadError as err:
                self.logger.error(
                    'Loading module `%s`: %s' % (path, err)
                )
                return
            self._experiments[experiment_name] = exp
        self.logger.info('Module `%s` is successfully loaded!' % path)

    def ls_exp(self, *args):
        args = list(args)

        try:
            experiment_name = args.pop(0)
            if experiment_name not in self._experiments:
                self.logger.error(
                    'Experiment `%s` is not loaded!' % experiment_name
                )
                return
            exp = self._experiments[experiment_name]
        except IndexError:
            self.logger.error('Please specify experiment name!')
            return

        tasks, runners = exp.get_contents()
        print '> Module `%s`:' % experiment_name
        if len(runners) > 0:
            print 'Runners:'
            print '\n'.join(runners)
        if len(tasks) > 0:
            print 'Tasks:'
            print '\n'.join(tasks)

    def run_exp(self, *args):
        """Runs a task or an experiment."""
        args = list(args)

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

        try:
            func_name = args.pop(0)
        except IndexError:
            func_name = 'run'  # default

        hosts = {}
        for inst in self.registry.get_instances_list(self.shell.get_session()):
            hosts[inst.get_host_string()] = inst

        res = exp.run(hosts.keys(), self.ssh_id_file_path, func_name,
                      args=args)
        if res is False:
            self.logger.error(
                'Task `%s.%s` failed!' % (experiment_name, func_name)
            )
