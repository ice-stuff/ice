"""EC2-like cloud related helper commands."""
from boto import ec2
from boto import exception as boto_exception


class CfgEC2CloudAuth(object):
    """EC2 cloud authentication parameters"""

    def __init__(self, ec2_url, aws_access_key, aws_secret_key):
        """Create an EC2 auth object.

        :param ec2_url string: EC2 URL or region.
        :param aws_access_key string: AWS access key.
        :param aws_secret_key string: AWS secret key.
        """
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


class CfgEC2VMSpec(object):
    """Specification of an EC2 VM"""

    def __init__(self, ami_id, ssh_key_name, flavor='t2.micro',
                 user_data=None, security_group_id=None, subnet_id=None):
        """Create an EC2 VM specification

        :param str ami_id: AWS image (AMI) id.
        :param str ssh_key_name: Name of the AWS SSH keypair.
        :param str flavor: AWS flavor. Optional, default: t2.micro.
        :param str user_data: User (contextualisation) data to pass over.
            Optional, default: None.
        :param str security_group_id: Id of AWS security group. Optional:
            default: None.
        :param str subnet_id: Id of the AWS subnet. Optional, default:
            None.
        """
        self.ami_id = ami_id
        self.ssh_key_name = ssh_key_name
        self.flavor = flavor
        self.user_data = user_data
        self.security_group_id = security_group_id
        self.subnet_id = subnet_id


class EC2Client(object):
    """EC2-like API client."""

    def __init__(self, auth, logger):
        """Create an EC2 client for a given authentication.

        :param ice.ec2_client.CfgEC2CloudAuth auth: EC2 authentication parameters.
        :param logging.Logger logger: Logger.
        """
        self.auth = auth
        self.logger = logger

    def create(self, amt, spec):
        """Creates a list of VMs.

        :param int amt: The number of VMs to create.
        :param ice.ec2_client.CfgEC2VMSpec spec: The specification of the VMs to
            launch.
        :return: The reservation or `None` in case of error.
        :rtype: boto.ec2.instance.Reservation
        """
        boto_kwargs = {
            'instance_type': spec.flavor,
            'key_name': spec.ssh_key_name,
            'min_count': amt,
            'max_count': amt
        }
        if spec.user_data is not None:
            boto_kwargs['user_data'] = spec.user_data
        if spec.security_group_id is not None:
            boto_kwargs['security_group_ids'] = [spec.security_group_id]
        if spec.subnet_id is not None:
            boto_kwargs['subnet_id'] = spec.subnet_id
        # if spec.vpc_id is not None:
        #     boto_kwargs['vpc_id'] = spec.vpc_id

        try:
            reservation = self.auth.get_conn().run_instances(
                spec.ami_id, **boto_kwargs
            )
            self.logger.debug(
                'Reservation {0.id:s} for {1:d} instances was created'.format(
                    reservation, amt
                )
            )
            return reservation
        except boto_exception.EC2ResponseError as err:
            self.logger.error('Failed to run instances: {}'.format(str(err)))
            return None

    def destroy(self, instance_ids=None):
        """Wait for instances of current session to come up.

        :param list of [str] instance_ids: List of instances to destroy. If not
            provided, all the instances in given cloud and session will be
            destroyed.
        :return: List of destroyed instances (`boto.ece2.instance.Instance`).
        :rtype: list of [boto.ece2.instance.Instance]
        """
        # Get list of instance ids
        if instance_ids is None or len(instance_ids) == 0:
            reservations = self.auth.get_conn().get_all_instances()
            instance_ids = []
            for reservation in reservations:
                for inst in reservation.instances:
                    if inst.state == 'terminated':
                        continue
                    elif inst.state == 'shutting-down':
                        continue
                    instance_ids.append(inst.id)

        if len(instance_ids) > 0:
            instances = self.auth.get_conn().terminate_instances(instance_ids)
        else:
            instances = []
        self.logger.debug(
            '{0:d} instances were terminated!'.format(len(instances))
        )

        return instances

    def get_list(self):
        """Returns list of current reservations.

        :return: List of active reservations (`boto.ece2.instance.Reservation`).
        :rtype: list of [boto.ece2.instance.Reservation]
        """
        try:
            reservations = self.auth.get_conn().get_all_instances()
            self.logger.debug(
                'Found {0:d} reservations'.format(len(reservations))
            )
            return reservations
        except boto_exception.EC2ResponseError as err:
            self.logger.error('Failed to list instances: {}'.format(str(err)))
            return None
