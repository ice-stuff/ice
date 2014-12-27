"""Wrapper class for EC2-like cloud related shell commands."""
import argparse

from . import ShellExt
from ice import api


class EC2Shell(ShellExt):

    """Wrapper class for EC2-like cloud related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        super(EC2Shell, self).__init__(shell)

        # Instances
        self._instances = {}

        # Register self
        shell.add_magic_function_v2(
            'ec2_ls', self.run_ls, self.get_ls_parser()
        )
        shell.add_magic_function_v2(
            'ec2_create', self.run_create, self.get_create_parser()
        )
        shell.add_magic_function_v2(
            'ec2_wait', self.run_wait, self.get_wait_parser()
        )
        shell.add_magic_function_v2(
            'ec2_destroy', self.run_destroy, self.get_destroy_parser()
        )

    #
    # Start / stop
    #

    def stop(self):
        super(EC2Shell, self).stop()

        # Build dictionary of lists of instance ids
        clouds = {}
        for inst_id, entry in self._instances.items():
            key = entry['cloud_id']
            if key not in clouds:
                clouds[key] = []
            clouds[key].append(inst_id)

        # Call APIs
        for cloud_id, instance_ids in clouds.items():
            api.ec2.destroy(instance_ids, cloud_id)

    #
    # Commands
    #

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

    def run_ls(self, magics, args_raw):
        """Lists EC2 instances."""
        args = self.get_ls_parser().parse_args(args_raw.split())

        # Call API to get the reservations
        reservations = api.ec2.get_list(args.cloud_id)

        # Print
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

    def run_create(self, magics, args_raw):
        """Creates new EC2 instances."""
        args = self.get_create_parser().parse_args(args_raw.split())

        # Launch VMs
        reservation = api.ec2.create(args.amt, args.ami_id, args.flavor,
                                     args.cloud_id)
        if reservation is None:
            self.logger.error('Failed to run instances!')
            return

        # Store VMs
        for inst in reservation.instances:
            self._instances[inst.id] = {
                'inst': inst,
                'cloud_id': args.cloud_id
            }

        # Print
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

    def run_wait(self, magics, args_raw):
        """Wait for 'pending' instances."""
        args = self.get_wait_parser().parse_args(args_raw.split())

        # Run the API-call
        res = api.ec2.wait(args.timeout, args.cloud_id)

        # Print
        if res:
            self.logger.info('No instances in pending state now!')
        else:
            self.logger.error('Timeout!')

    def get_destroy_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_parser', add_help=False)
        parser.add_argument(
            '-i', metavar='<Instance Id>', dest='instance_ids', nargs='+'
        )
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id', default=None
        )
        return parser

    def run_destroy(self, magics, args_raw):
        """Destroys existing EC2 instances."""
        args = self.get_destroy_parser().parse_args(args_raw.split())

        # Destroy VMs
        instances = api.ec2.destroy(args.instance_ids, args.cloud_id)

        # De-register them from internal structure
        for inst in instances:
            del self._instances[inst.id]

        # Print
        self._print_instances(instances)

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
