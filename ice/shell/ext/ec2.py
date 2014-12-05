"""Wrapper class for EC2-like cloud related shell commands."""
import argparse
import base64

from boto import exception as boto_exception
from boto import ec2

from . import ShellExt


class EC2Shell(ShellExt):
    """Wrapper class for EC2-like cloud related shell commands."""

    def __init__(self, shell):
        """
        :param ice.shell.Shell shell: The shell.
        """
        super(EC2Shell, self).__init__(shell)

        # Parse configuration
        self._clouds, self.default_cloud_id = self._parse_clouds(self.config)
        if len(self._clouds) == 0:
            self.logger.error('No clouds found in configuration!')
        self.cfg_api_host = self.config.get_str(
            'shell', 'api_host', required=True
        )
        self.cfg_api_port = self.config.get_int('shell', 'api_port', 80)

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
            'ec2_destroy', self.run_destroy, self.get_destroy_parser()
        )

    #
    # Start / stop
    #

    def stop(self):
        super(EC2Shell, self).stop()

        # Destroy instances
        instances_id = []
        for inst_id, entry in self._instances.items():
            entry['cloud']['conn'].terminate_instances([entry['inst'].id])

    #
    # Commands
    #

    def get_ls_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_ls', add_help=False)
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id',
            default=self.default_cloud_id
        )
        parser.add_argument(
            '-s', action='store_true', dest='show_reservations',
            help='Show reservation ids.', default=False
        )
        return parser

    def run_ls(self, magics, args_raw):
        """Lists EC2 instances."""
        args = self.get_ls_parser().parse_args(args_raw.split())

        # Look for cloud
        cloud = self._clouds.get(args.cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(args.cloud_id))
            return

        # List instances
        resp = cloud['conn'].get_all_instances()

        # Print
        self._print_reservations(resp, args.show_reservations)

    def get_create_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_create', add_help=False)
        parser.add_argument(
            '-n', type=int, metavar='<Amount>', dest='amt', default=1
        )
        parser.add_argument('-i', metavar='<AMI Id>', dest='ami_id')
        parser.add_argument('-t', metavar='<Type>', dest='flavor')
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id',
            default=self.default_cloud_id
        )
        return parser

    def run_create(self, magics, args_raw):
        """Creates new EC2 instances."""
        args = self.get_create_parser().parse_args(args_raw.split())

        # Look for cloud
        cloud = self._clouds.get(args.cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(args.cloud_id))
            return

        # Compile user data
        user_data = self._compile_user_data()

        # Define arguments
        ami_id = args.ami_id
        if ami_id is None:
            ami_id = cloud['default_ami_id']
        kwargs = {}
        kwargs['instance_type'] = args.flavor
        if kwargs['instance_type'] is None:
            kwargs['instance_type'] = cloud['default_flavor']
        kwargs['key_name'] = cloud['ssh_key_name']
        kwargs['min_count'] = args.amt
        kwargs['max_count'] = args.amt
        kwargs['user_data'] = user_data
        if cloud['sg_name'] is not None:
            kwargs['security_groups'] = [cloud['sg_name']]
        if ['sg_id'] is not None:
            kwargs['security_group_ids'] = [cloud['sg_id']]
        if cloud['subnet_id'] is not None:
            kwargs['subnet_id'] = cloud['subnet_id']
        # if cloud['vpc_id'] is not None:
        # kwargs['vpc_id'] = cloud['vpc_id']

        # Run
        try:
            resp = cloud['conn'].run_instances(ami_id, **kwargs)

            # Add instances
            for inst in resp.instances:
                self._instances[inst.id] = {
                    'inst': inst,
                    'cloud': cloud
                }

            # Print
            self._print_reservations([resp])
        except boto_exception.EC2ResponseError as err:
            self.logger.error('Failed to run instances: {}'.format(str(err)))

    def get_destroy_parser(self):
        parser = argparse.ArgumentParser(prog='ec2_parser', add_help=False)
        parser.add_argument(
            '-i', metavar='<Instance Id>', dest='instance_ids', nargs='+'
        )
        parser.add_argument(
            '-c', metavar='<Cloud Id>', dest='cloud_id',
            default=self.default_cloud_id
        )
        return parser

    def run_destroy(self, magics, args_raw):
        """Destroys existing EC2 instances."""
        args = self.get_destroy_parser().parse_args(args_raw.split())

        # Look for cloud
        cloud = self._clouds.get(args.cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(args.cloud_id))
            return

        # Get list of instance ids
        if args.instance_ids is not None and len(args.instance_ids) > 0:
            instance_ids = args.instance_ids
        else:
            # Load all instances
            reservations = cloud['conn'].get_all_instances()
            instance_ids = []
            for reservation in reservations:
                for inst in reservation.instances:
                    if inst.state == 'terminated':
                        continue
                    elif inst.state == 'shutting-down':
                        continue
                    instance_ids.append(inst.id)

        # Destroy instances
        if len(instance_ids) > 0:
            instances = cloud['conn'].terminate_instances(instance_ids)
        else:
            instances = []
        for inst in instances:
            if inst.id in self._instances:
                del self._instances[inst.id]
        self._print_instances(instances)

    #
    # Helpers
    #

    def _parse_clouds(self, config):
        # Fetch cloud ids
        tci = config.get_str('ec2', 'clouds', '').split(',')
        cloud_ids = []
        for c in tci:  # remove empty string
            if c != '': cloud_ids.append(c)
        if len(cloud_ids) == 0:
            return [], None

        # Initialize connections
        clouds = {}

        for cloud_id in cloud_ids:
            cloud = {}

            # Load configuration
            cfg = config.get_dict('ec2_{}'.format(cloud_id))

            # Select default flavor
            cloud['default_flavor'] = cfg.get(
                'default_flavor',
                config.get_str('ec2', 'default_flavor', 't2.micro')
            )

            # Initialize Boto connection
            try:
                # Load configuration
                cloud['sg_id'] = cfg.get('security_group_id', None)
                cloud['sg_name'] = cfg.get('security_group_name', None)
                cloud['subnet_id'] = cfg.get('subnet_id', None)
                cloud['vpc_id'] = cfg.get('vpc_id', None)
                cloud['ssh_key_name'] = cfg['ssh_key_name']
                cloud['default_ami_id'] = cfg['default_ami_id']
                ec2_url = cfg['region']
                aws_access_key_id = cfg['aws_access_key']
                aws_secret_key = cfg['aws_secret_key']

                # Initiate connection
                cloud['conn'] = ec2.connect_to_region(
                    ec2_url,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_key
                )
                if cloud['conn'] is None:  # Connection failed!
                    self.logger.error(
                        'Failed to setup Boto connection with'
                        + ' cloud `{}`'.format(cloud_id)
                    )
                    continue
            except KeyError as err:  # a configuration option is missing
                self.logger.error(
                    'Option `{}` not found in `ec2_{}` section!'.format(
                        str(err.args[0]), cloud_id
                    )
                )
                continue

            # Append cloud to list
            clouds[cloud_id] = cloud

        return clouds, cloud_ids[0]

    def _compile_user_data(self):
        session_id = self.current_session.id
        user_data = """#!/bin/bash

curl https://raw.githubusercontent.com/glestaris/iCE/master/agent/ice-register-self.py -O ./ice-register-self.py
chmod +x ./ice-register-self.py
./ice-register-self.py -a http://{0:s}:{1:d} -s {2:s}

""".format(self.cfg_api_host, self.cfg_api_port, session_id)
        return base64.b64encode(user_data)

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
            'Public IP DNS',
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
            'Public IP DNS',
            'Status',
            'Launched on'
        )
        print '-' * 129
        for inst in instances:
            print self._format_instance(inst)
        print '-' * 129
