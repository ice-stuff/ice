"""Wrapper class for EC2-like cloud related shell commands."""
import argparse
from ice import ec2_client
from . import ShellExt


class EC2Shell(ShellExt):
    """Wrapper class for EC2-like cloud related shell commands."""

    def __init__(self, cfg_factory, registry, public_reg_host, public_reg_port,
                 logger, debug=False):
        """
        :param ice.config.ConfigFactory cfg_factory:
        :param ice.registry.client.RegistryClient registry:
        :param string public_reg_host:
        :param int public_reg_port:
        :param logging.Logger logger:
        :param bool debug: Set to True for debug behaviour.
        """
        self.cfg_factory = cfg_factory
        self.registry = registry
        self.public_reg_host = public_reg_host
        self.public_reg_port = public_reg_port
        self.retain_vms = False
        self._instances = {}
        super(EC2Shell, self).__init__(logger, debug)

    def start(self, shell):
        """Starts the shell extension.

        It initializes the extension object and calls the
        shell.add_command to setup the shell hooks.

        :param ice.shell.Shell shell:
        """
        super(EC2Shell, self).start(shell)

        shell.add_command(
            'ec2_ls', self.run_ls,
            parser=self.get_ls_parser()
        )
        shell.add_command(
            'ec2_create', self.run_create,
            parser=self.get_create_parser()
        )
        # shell.add_command(
        #     'ec2_wait', self.run_wait,
        #     parser=self.get_wait_parser()
        # )
        shell.add_command(
            'ec2_destroy', self.run_destroy,
            parser=self.get_destroy_parser()
        )
        shell.add_command(
            'ec2_retain_vms', self.run_retain_vms,
            usage='When called, iCE will not destroy EC2 VMs on exit.'
        )

    def stop(self):
        """Stops the extension. It cleans up the state of the extension."""
        super(EC2Shell, self).stop()

        if self.retain_vms:
            return

        clouds = {}
        for inst_id, entry in self._instances.items():
            key = entry['cloud_id']
            if key not in clouds:
                clouds[key] = []
            clouds[key].append(inst_id)

        for cloud_id, instance_ids in clouds.items():
            self._get_client(cloud_id).destroy(instance_ids)

    def _get_spec(self, cloud_id=None):
        if cloud_id is None:
            cloud_ids = self.cfg_factory.get_ec2_cloud_ids()
            if len(cloud_ids) == 0:
                return None
            cloud_id = cloud_ids[0]

        return self.cfg_factory.get_ec2_vm_spec(cloud_id)

    def _get_client(self, cloud_id=None):
        if cloud_id is None:
            cloud_ids = self.cfg_factory.get_ec2_cloud_ids()
            if len(cloud_ids) == 0:
                return None
            cloud_id = cloud_ids[0]

        return ec2_client.EC2Client(
            self.cfg_factory.get_ec2_cloud_auth(cloud_id),
            self.logger
        )

    def get_ls_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_ls', add_help=False)
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id', default=None
        )
        parser.add_argument(
            '-s', action='store_true', dest='show_reservations',
            help='Show reservation ids.', default=False
        )
        return parser

    def run_ls(self, args):
        """Lists EC2 instances."""
        reservations = self._get_client(args.cloud_id).get_list()

        self._print_reservations(reservations, args.show_reservations)

    def get_create_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_create', add_help=False)
        parser.add_argument(
            '-n', type=int, metavar='<Amount>', dest='amt', default=1
        )
        parser.add_argument('-i', metavar='<AMI Id>', dest='ami_id')
        parser.add_argument('-t', metavar='<Type>', dest='flavor')
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id', default=None
        )
        return parser

    def run_create(self, args):
        """Creates new EC2 instances."""
        spec = self._get_spec(args.cloud_id)
        if args.ami_id is not None:
            spec.ami_id = args.ami_id
        if args.flavor is not None:
            spec.flavor = args.flavor

        spec.user_data = self.registry.compile_user_data(
            self.shell.get_session(),
            self.public_reg_host,
            self.public_reg_port
        )

        reservation = self._get_client(args.cloud_id).create(args.amt, spec)
        if reservation is None:
            self.logger.error('Failed to run instances!')
            return

        for inst in reservation.instances:
            self._instances[inst.id] = {
                'inst': inst,
                'cloud_id': args.cloud_id
            }
        self._print_reservations([reservation])

    def get_wait_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_wait', add_help=False)
        parser.add_argument(
            '-t', metavar='<Timeout (sec.)>', dest='timeout', default=120
        )
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id', default=None
        )
        return parser

    # def run_wait(self, args):
    #     """Wait for 'pending' instances."""
    #     res = api.ec2.wait(args.timeout, args.cloud_id)

    #     if res:
    #         self.logger.info('No instances in pending state now!')
    #     else:
    #         self.logger.error('Timeout!')

    def get_destroy_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_parser', add_help=False)
        parser.add_argument(
            '-i', metavar='<Instance Id>', dest='instance_ids', nargs='+'
        )
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id', default=None
        )
        return parser

    def run_destroy(self, args):
        """Destroys existing EC2 instances."""
        instances = self._get_client(args.cloud_id).destroy(args.instance_ids)

        for inst in instances:
            if inst.id in self._instances:
                del self._instances[inst.id]

        self._print_instances(instances)

    def run_retain_vms(self):
        """When called, iCE will not destroy EC2 VMs on exit."""
        self.retain_vms = True

    #
    # Helpers
    #

    def _format_instance(self, inst):
        """Formats an instance to be printed in a table.
        :param boto.ec2.instance.Instance inst: The EC2 instance.
        :rtype: str
        :return: A string.
        """
        ret_val = '| {0.id:15s} | {0.image_id:15s}'.format(inst) \
                  + ' | {0.instance_type:15s} | {0.ip_address:20s}'.format(inst) \
                  + ' | {0.state:15s} | {0.launch_time:30s} |'.format(inst)
        return ret_val

    def _print_reservations(self, reservations, show_reservations=True):
        """Prints a list of reservations.
        :param list of [boto.ec2.instance.Reservation] reservations: The
            reservations.
        :param bool show_reservations: Show the reservation names.
        """
        print '-' * 129
        print '| {0:15s} | {1:15s} | {2:15s} | {3:20s} | {4:15s} | {5:30s} |' \
            .format(
                'Id',
                'AMI Id',
                'Instance type',
                'Public IP',
                'Status',
                'Launched on'
            )
        print '-' * 129
        for reservation in reservations:
            if show_reservations:
                print '-' * 129
                print '| Reservation: {0.id:20s} {1}|'.format(
                    reservation, ' ' * 92
                )
                print '-' * 129
            for inst in reservation.instances:
                print self._format_instance(inst)
        print '-' * 129

    def _print_instances(self, instances):
        """Prints a list of instances.
        :param list of [boto.ec2.instance.Instance] instances: The
            instances.
        """
        print '-' * 129
        print '| {0:15s} | {1:15s} | {2:15s} | {3:20s} | {4:15s} | {5:30s} |' \
            .format(
                'Id',
                'AMI Id',
                'Instance type',
                'Public IP',
                'Status',
                'Launched on'
            )
        print '-' * 129
        for inst in instances:
            print self._format_instance(inst)
        print '-' * 129
