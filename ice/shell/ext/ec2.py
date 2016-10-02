"""Wrapper class for EC2-like cloud related shell commands."""
import argparse
from ice import ec2_client
from ice import ascii_table
from . import ShellExt


class EC2Shell(ShellExt):
    """Wrapper class for EC2-like cloud related shell commands."""

    def __init__(self, cfg_factory, registry, logger, debug=False):
        """
        :param ice.config.ConfigFactory cfg_factory:
        :param ice.registry.client.RegistryClient registry:
        :param logging.Logger logger:
        :param bool debug: Set to True for debug behaviour.
        """
        self.cfg_factory = cfg_factory
        self.registry = registry
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
        shell.add_command(
            'ec2_destroy', self.run_destroy,
            parser=self.get_destroy_parser()
        )
        shell.add_command(
            'ec2_release_vms', self.run_release_vms,
            usage='When called, iCE will destroy EC2 VMs on exit.'
        )
        shell.add_command(
            'ec2_retain_vms', self.run_retain_vms,
            usage='When called, iCE will not destroy EC2 VMs on exit.'
        )

    def stop(self):
        """Stops the extension. It cleans up the state of the extension."""
        super(EC2Shell, self).stop()

        if len(self._instances) == 0:
            return

        if self.retain_vms:
            self.logger.debug(
                'EC2 VMs will not be deleted, since they are retained'
            )
            return

        clouds = {}
        for inst_id, entry in self._instances.items():
            key = entry['cloud_id']
            if key not in clouds:
                clouds[key] = []
            clouds[key].append(inst_id)

        for cloud_id, instance_ids in clouds.items():
            self._get_client(cloud_id).destroy(instance_ids)
        self.logger.info(
            '%s EC2 VMs were successfully deleted.' % len(self._instances)
        )

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

        table = self._get_instances_table()

        for res in reservations:
            table.add_comment_row('Resrvation: {:s}'.format(res.id))
            for inst in res.instances:
                table.add_row({
                    'id': inst.id,
                    'instance_type': inst.instance_type,
                    'ip_address': inst.ip_address,
                    'state': inst.state
                })

        self._render_instances_table(table)

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
            self.shell.get_session(), self.cfg_factory.get_registry_client()
        )

        reservation = self._get_client(args.cloud_id).create(args.amt, spec)
        if reservation is None:
            self.logger.error('Failed to run instances!')
            return

        table = self._get_instances_table()
        table.add_comment_row('Resrvation: {:s}'.format(reservation.id))

        for inst in reservation.instances:
            self._instances[inst.id] = {
                'inst': inst,
                'cloud_id': args.cloud_id
            }

            table.add_row({
                'id': inst.id,
                'instance_type': inst.instance_type,
                'ip_address': inst.ip_address,
                'state': inst.state
            })

        self._render_instances_table(table)

    def get_wait_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_wait', add_help=False)
        parser.add_argument(
            '-t', metavar='<Timeout (sec.)>', dest='timeout', default=120
        )
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id', default=None
        )
        return parser

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

        table = self._get_instances_table()
        for inst in instances:
            if inst.id in self._instances:
                del self._instances[inst.id]
            table.add_row({
                'id': inst.id,
                'instance_type': inst.instance_type,
                'ip_address': inst.ip_address,
                'state': inst.state
            })
        self._render_instances_table(table)

    def run_release_vms(self):
        """When called, iCE will destroy EC2 VMs on exit."""
        self.retain_vms = False

    def run_retain_vms(self):
        """When called, iCE will not destroy EC2 VMs on exit."""
        self.retain_vms = True

    #
    # Helpers
    #

    def _get_instances_table(self):
        table = ascii_table.ASCIITable()

        table.add_column('id', ascii_table.ASCIITableColumn('Id', 23))
        table.add_column('instance_type',
                         ascii_table.ASCIITableColumn('Instance type', 18))
        table.add_column('ip_address',
                         ascii_table.ASCIITableColumn('Public IP', 23))
        table.add_column('state', ascii_table.ASCIITableColumn('State', 16))

        return table

    def _render_instances_table(self, table):
        print ascii_table.ASCIITableRenderer().render(table)
