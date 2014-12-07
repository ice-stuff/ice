"""Wrapper class for API-related shell commands."""
from . import ShellExt
from ice import api_client
from ice import api


class APIShell(ShellExt):
    """Wrapper class for API-related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        super(APIShell, self).__init__(shell)
        self.api_client = api_client.APIClient(
            self.config.get_str('api_client', 'host', 'localhost'),
            self.config.get_int('api_client', 'port', 5000)
        )

        # Register self
        shell.add_magic_function('inst_ls', self.ls_inst)
        shell.add_magic_function(
            'inst_del', self.del_inst,
            usage='<Instance id> [<Instance id> ...]'
        )
        shell.add_magic_function(
            'inst_show', self.show_inst,
            usage='<Instance id> [<Instance id> ...]'
        )

    #
    # Commands
    #

    def ls_inst(self, magis, args_raw):
        """Lists instances."""
        # Get instances
        inst_list = self.api_client.get_instances_list(
            api.session.get_current_session().id)
        if inst_list is None:
            self.logger.error('Failed to find instances!')
            return

        self.logger.info('Found %d instances' % len(inst_list))
        print '-' * 129
        print '| {0:23s} | {1:20s} | {2:43s} | {3:30s} |'.format(
            'Id',
            'Public IP address',
            'Cloud Id',
            'Created on'
        )
        print '-' * 129
        for inst in inst_list:
            print '| {0.id:23s} | {0.public_ip_addr:20s}'.format(inst) \
                  + ' | {0.cloud_id:43s} | {0.created:30s} |'.format(inst)
        print '-' * 129

    def show_inst(self, magics, args_raw):
        """Shows information for a specific instance."""
        inst_ids = args_raw.split()

        # Check arguments
        if len(inst_ids) == 0:
            self.logger.error('Please specify instance id!')
            return

        # Get instance
        for inst_id in inst_ids:
            inst = self.api_client.get_instance(inst_id)
            if inst is None:
                self.logger.error('Failed to find instance `%s`!' % inst_id)
                return

            # Printout information
            for key, value in inst.__dict__.items():
                print '{0:30s}: {1}'.format(key, value)

    def del_inst(self, magics, args_raw):
        """Deletes a specific instance."""
        inst_ids = args_raw.split()

        # Check arguments
        if len(inst_ids) == 0:
            self.logger.error('Please specify instance id!')
            return

        # Fire action
        for inst_id in inst_ids:
            if not self.api_client.delete_instance(inst_id):
                self.logger.error('Failed to delete instance `%s`' % inst_id)
                return
            self.logger.info(
                'Instance `%s` was successfully deleted!' % inst_id
            )
