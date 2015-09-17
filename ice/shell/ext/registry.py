"""Wrapper class for registry-related shell commands."""
import argparse
from . import ShellExt


class RegistryShell(ShellExt):
    """Wrapper class for registry-related shell commands."""

    def __init__(self, registry, logger, debug=False):
        """
        :param ice.registry.client.RegistryClient registry:
        :param logging.Logger logger:
        :param bool debug: Set to True for debug behaviour.
        """
        self.registry = registry
        super(RegistryShell, self).__init__(logger, debug)

    def start(self, shell):
        """Starts the shell extension.

        It initializes the extension object and calls the
        shell.add_command to setup the shell hooks.

        :param ice.shell.Shell shell:
        """
        super(RegistryShell, self).start(shell)
        shell.add_command('inst_ls', self.ls_inst)
        # shell.add_command(
        #     'inst_wait', self.run_wait,
        #     parser=self.get_wait_parser()
        # )
        shell.add_command(
            'inst_del', self.del_inst,
            usage='<Instance id> [<Instance id> ...]'
        )
        shell.add_command(
            'inst_show', self.show_inst,
            usage='<Instance id> [<Instance id> ...]'
        )

    def ls_inst(self):
        """Lists instances."""
        inst_list = self.registry.get_instances_list(
            self.shell.get_session()
        )
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

    # def get_wait_parser(self):
    #     parser = argparse.ArgumentParser(prog='inst_wait', add_help=False)
    #     parser.add_argument(
    #         '-n', metavar='<Amount of instances>', dest='amt', type=int,
    #         default=1
    #     )
    #     parser.add_argument(
    #         '-t', metavar='<Timeout (sec.)>', dest='timeout', default=120
    #     )
    #     return parser

    # def run_wait(self, *args):
    #     """Waits for instances to appear."""
    #     args = self.get_wait_parser().parse_args(args_raw.split())
    #     res = api.instances.wait(args.amt, args.timeout)
    #     if res:
    #         self.logger.info('Instances are ready!')
    #     else:
    #         self.logger.error('Timeout!')

    def show_inst(self, *inst_ids):
        """Shows information for a specific instance."""
        if len(inst_ids) == 0:
            self.logger.error('Please specify an instance id!')
            return

        for inst_id in inst_ids:
            inst = self.registry.get_instance(inst_id)
            if inst is None:
                self.logger.error('Failed to find instance `%s`!' % inst_id)
                continue

            # Printout information
            for key, value in inst.__dict__.items():
                print '{0:30s}: {1}'.format(key, value)

    def del_inst(self, *inst_ids):
        """Deletes a specific instance."""
        if len(inst_ids) == 0:
            self.logger.error('Please specify an instance id!')
            return

        for inst_id in inst_ids:
            if not self.registry.delete_instance(inst_id):
                self.logger.error('Failed to find instance `%s`!' % inst_id)
                continue
            else:
                self.logger.info(
                    'Instance `%s` was successfully deleted.' % inst_id
                )
