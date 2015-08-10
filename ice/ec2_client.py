"""EC2-like cloud related helper commands."""
import time

from boto import ec2
from boto import exception as boto_exception


class EC2CloudAuth(object):
    """EC2 cloud authentication parameters

    :type ec2_url: string
    :type aws_access_key: string
    :type aws_secret_key: string
    """

    def __init__(self, ec2_url, aws_access_key, aws_secret_key):
        self.ec2_url = ec2_url
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self._conn = None

    def get_conn(self):
        if self._conn is None:
            self._conn = ec2.connect_to_region(
                self.ec2_url,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )

        return self._conn


class EC2Client(object):

    """EC2-like API client.

    :type config: ice.config.Configuration
    :type logger: logging.logger
    :type clouds: dict
    :type default_cloud_id: str
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        # Parse configuration
        self.clouds, self.default_cloud_id = self._parse_cloud_configuration()

    def create(self, amt, user_data=None, ami_id=None, flavor=None,
               cloud_id=None):
        """Creates a list of VMs.

        :param int amt: The number of VMs to create.
        :param str user_data: The user data to pass to the VM.
        :param str ami_id: The AMI Id to use.
        :param str flavor: The instances flavor (instance type).
        :param str cloud_id: The id of the cloud to use.
        :rtype: boto.ec2.instance.Reservation
        :return: The reservation or `None` in case of error.
        """
        # Look for cloud
        if cloud_id is None:
            cloud_id = self.default_cloud_id
        cloud = self.clouds.get(cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(cloud_id))
            return None

        # Define arguments
        if ami_id is None:
            ami_id = cloud['default_ami_id']
        boto_kwargs = {
            'instance_type': flavor,
            'key_name': cloud['ssh_key_name'],
            'min_count': amt,
            'max_count': amt
        }
        if boto_kwargs['instance_type'] is None:
            boto_kwargs['instance_type'] = cloud['default_flavor']
        if user_data is not None:
            boto_kwargs['user_data'] = user_data
        if cloud['sg_name'] is not None:
            boto_kwargs['security_groups'] = [cloud['sg_name']]
        if ['sg_id'] is not None:
            boto_kwargs['security_group_ids'] = [cloud['sg_id']]
        if cloud['subnet_id'] is not None:
            boto_kwargs['subnet_id'] = cloud['subnet_id']
        # if cloud['vpc_id'] is not None:
        # boto_kwargs['vpc_id'] = cloud['vpc_id']

        # Run
        try:
            reservation = cloud['conn'].run_instances(ami_id, **boto_kwargs)
            self.logger.debug(
                'Reservation {0.id:s} for {1:d} instances was created'.format(
                    reservation, amt
                )
            )
            return reservation
        except boto_exception.EC2ResponseError as err:
            self.logger.error('Failed to run instances: {}'.format(str(err)))
            return None

    def wait(self, timeout=120, cloud_id=None):
        """Wait for instances of current session to come up.

        :param int timeout: The number of seconds to wait before returning
            `False`.
        :param str cloud_id: The id of the cloud to use.
        :rtype: bool
        :return: `False` if timeout was exceeded. `True` if everything went
            well.
        """
        # Look for cloud
        if cloud_id is None:
            cloud_id = self.default_cloud_id
        cloud = self.clouds.get(cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(cloud_id))
            return False

        # Check reservations
        try:
            seconds = 0
            while seconds < timeout:
                reservations = cloud['conn'].get_all_instances()

                loop_again = False
                for reservation in reservations:
                    for instance in reservation.instances:
                        if instance.state == 'pending':
                            self.logger.debug(
                                'Instance {0.id} is in status pending...'
                                .format(instance)
                            )
                            loop_again = True
                            break
                    if loop_again:
                        break
                if loop_again:
                    seconds += 5
                    self.logger.debug('Sleeping for 5 seconds...')
                    time.sleep(5)
                    continue
                return True

            return False
        except boto_exception.EC2ResponseError as err:
            self.logger.error(
                'Failed to check on instances: {}'.format(str(err)))
            return False

    def destroy(self, instance_ids=None, cloud_id=None):
        """Wait for instances of current session to come up.

        :param list of [str] instance_ids: List of instances to destroy. If not
            provided, all the instances in given cloud and session will be
            destroyed.
        :param str cloud_id: The id of the cloud to use.
        :rtype: list of [boto.ece2.instance.Instance]
        :return: List of destroyed instances (`boto.ece2.instance.Instance`).
        """
        # Look for cloud
        if cloud_id is None:
            cloud_id = self.default_cloud_id
        cloud = self.clouds.get(cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(cloud_id))
            return []

        # Get list of instance ids
        if instance_ids is None or len(instance_ids) == 0:
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
        self.logger.debug(
            '{0:d} instances were terminated!'.format(len(instances))
        )

        return instances

    def get_list(self, cloud_id=None):
        """Returns list of current reservations.

        :param str cloud_id: The id of the cloud to use.
        :rtype: list of [boto.ece2.instance.Reservation]
        :return: List of active reservations (`boto.ece2.instance.Reservation`).
        """
        # Look for cloud
        if cloud_id is None:
            cloud_id = self.default_cloud_id
        cloud = self.clouds.get(cloud_id, None)
        if cloud is None:
            self.logger.error('Failed to use cloud {}'.format(cloud_id))
            return []

        # Run
        try:
            reservations = cloud['conn'].get_all_instances()
            self.logger.debug(
                'Found {0:d} reservations'.format(len(reservations))
            )
            return reservations
        except boto_exception.EC2ResponseError as err:
            self.logger.error('Failed to list instances: {}'.format(str(err)))
            return None

    #
    # Helpers
    #

    def _parse_cloud_configuration(self):
        # Fetch cloud ids
        tci = self.config.get_str('ec2', 'clouds', '').split(',')
        cloud_ids = []
        for c in tci:  # remove empty string
            if c != '':
                cloud_ids.append(c)
        if len(cloud_ids) == 0:
            return {}, None

        # Credentials
        aws_access_key_id = self.config.get_str('ec2', 'aws_access_key', '')
        aws_secret_key = self.config.get_str('ec2', 'aws_secret_key', '')

        # Initialize connections
        clouds = {}

        for cloud_id in cloud_ids:
            cloud = {}

            # Load configuration
            cloud_cfg = self.config.get_dict('ec2_{}'.format(cloud_id))

            # Select default flavor
            cloud['default_flavor'] = cloud_cfg.get(
                'default_flavor',
                self.config.get_str('ec2', 'default_flavor', 't2.micro')
            )

            # Initialize Boto connection
            try:
                # Load configuration
                cloud['sg_id'] = cloud_cfg.get('security_group_id', None)
                cloud['sg_name'] = cloud_cfg.get('security_group_name', None)
                cloud['subnet_id'] = cloud_cfg.get('subnet_id', None)
                cloud['vpc_id'] = cloud_cfg.get('vpc_id', None)
                cloud['ssh_key_name'] = cloud_cfg['ssh_key_name']
                cloud['default_ami_id'] = cloud_cfg['default_ami_id']

                # URL
                if 'region' in cloud_cfg:
                    ec2_url = cloud_cfg['region']
                elif 'url' in cloud_cfg:
                    ec2_url = cloud_cfg['url']
                else:
                    ec2_url = cloud_id

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
