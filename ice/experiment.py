"""Experiment class module."""
import os
import sys
import types

from fabric import api as fabric_api

import ice


class Experiment(object):
    """Experiment class.

    :type logger: logging.Logger
    :type api_client: ice.api_client.APIClient
    :type session: ice.entities.Session
    :type module: module
    :type mod_name: str
    :type mod_file_path : str
    """

    class LoadError(Exception):
        pass

    def __init__(self, logger, session, api_client, file_path):
        """Constructs a new experiment.

        :param logging.Logger logger: The logger object.
        :param ice.entities.Session session: The current session.
        :param ice.api_client.APIClient api_client: iCE API client.
        :param str file_path: File path to the experiment file.
        :raises ice.experiment.Experiment.LoadError: If module fails to load.
        """
        self.logger = logger
        self.api_client = api_client
        self.session = session

        # Open experiment file
        if not os.path.isfile(file_path):
            raise Experiment.LoadError(
                'File {0:s} is not found!'.format(file_path)
            )
        if not file_path.endswith('.py'):
            raise Experiment.LoadError(
                'File {0:s} does not seem to be a Python file!'.format(
                    file_path
                )
            )
        self.mod_file_path = file_path
        self.mod_name = os.path.basename(self.mod_file_path).replace(
            '.py', ''
        )

        # Load module
        self.module = None
        self.load()

    def load(self):
        """Loads the module.

        :raises ice.experiment.Experiment.LoadError: If module fails to load.
        """
        # Setup Python path
        sys_path_changed = False
        parent_dir_path = os.path.abspath(os.path.dirname(self.mod_file_path))
        if parent_dir_path not in sys.path:
            sys_path_changed = True
            sys.path.append(parent_dir_path)

        # Load the module
        self.logger.debug(
            'About to load module \'{0:s}\' from path \'{1:s}\''
            .format(self.mod_name, parent_dir_path)
        )
        try:
            # Load or re-load module
            if self.module is None:
                self.module = __import__(self.mod_name)
            else:
                self.module = reload(self.module)

            # Check if module is loaded
            if self.module is None:
                raise Experiment.LoadError(
                    'File {0:s} was not loaded properly!'.format(
                        self.mod_file_path
                    )
                )
        except ImportError as err:  # error while parsing module
            raise Experiment.LoadError(
                'File {0:s} caused error: {1:s}'.format(
                    self.mod_file_path, str(err)
                )
            )

        # Reset python path
        if sys_path_changed:
            del sys.path[len(sys.path) - 1]  # Hack!

    def get_contents(self):
        """Lists the contents of the experiment module.

        :rtype: tuple
        :return: A tuple of lists. Tasks in the first element and runners in
            the second.
        """
        # Get strings (lines)
        runners = []
        tasks = []
        for entry, ob in self.module.__dict__.items():
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

        return tasks, runners

    def get_tasks(self):
        """Lists the tasks of the experiment module.

        :rtype: list
        :return: The list of tasks.
        """
        tasks, runners = self.get_contents()
        return tasks

    def get_runners(self):
        """Lists the runners of the experiment module.

        :rtype: list
        :return: The list of runners.
        """
        tasks, runners = self.get_contents()
        return runners

    def run(self, func_name=None, args=None):
        """Runs a task of runner of the experiment.

        :param str func_name: The name of the function (task or runner) to run.
        :param list args: List of arguments to pass
        :rtype: mixed
        :return: The result of the task or runner or `False` if function is not
            found.
        """

        # Fetch hosts
        hosts = {}
        instances = self.api_client.get_instances_list(self.session.id)
        for inst in instances:
            host_string = inst.get_host_string()
            hosts[host_string] = inst

        # Is task there?
        if func_name is None:
            func_name = 'run'
        try:
            func = getattr(self.module, func_name)
            if not isinstance(func, ice.Callable):
                self.logger.error(
                    'Attribute `%s.%s` is not a callable!'
                    % (self.mod_name, func_name)
                )
                return
        except AttributeError:
            self.logger.error(
                'Callable `%s.%s` is not found!' % (self.mod_name, func_name)
            )
            return

        # Execute
        with fabric_api.settings(hosts=hosts.keys()):
            # Prepare arguments
            if args is None:
                args = [hosts]
            elif isinstance(args, types.ListType):
                args = [hosts] + args
            else:
                args = [hosts] + list(args)

            # Run
            if isinstance(func, ice.Runner):
                return func(*args)
            elif isinstance(func, ice.Task):
                return fabric_api.execute(func, *args)
            else:
                return False
