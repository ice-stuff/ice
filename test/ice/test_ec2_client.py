import unittest2
import mock
from boto import ec2 as boto_ec2
from boto import exception as boto_exception
from ice import ec2_client
from test.ice.logger import get_logger


class TestCfgEC2CloudAuth(unittest2.TestCase):
    def setUp(self):
        self.ec2_ctr = boto_ec2.connect_to_region
        boto_ec2.connect_to_region = mock.MagicMock()
        boto_ec2.connect_to_region.return_value = object()

        self.cloud_auth = ec2_client.CfgEC2CloudAuth(
            'banana.aws.com',
            'IAmABanana',
            'IAmASecretBanana'
        )

    def tearDown(self):
        boto_ec2.connect_to_region = self.ec2_ctr

    def test_get_conn(self):
        self.assertIsNotNone(self.cloud_auth.get_conn())

        boto_ec2.connect_to_region.assert_called_once_with(
            'banana.aws.com',
            aws_access_key_id='IAmABanana',
            aws_secret_access_key='IAmASecretBanana'
        )

    def test_get_conn_cache(self):
        conn_a = self.cloud_auth.get_conn()
        conn_b = self.cloud_auth.get_conn()
        self.assertEqual(conn_a, conn_b)

        self.assertEqual(boto_ec2.connect_to_region.call_count, 1)


class TestEC2Client(unittest2.TestCase):
    def setUp(self):
        self.cloud_auth = ec2_client.CfgEC2CloudAuth(
            'banana.aws.com',
            'IAmABanana',
            'IAmASecretBanana'
        )

        self.ec2_conn = mock.MagicMock()
        self.cloud_auth.get_conn = mock.MagicMock(return_value=self.ec2_conn)

        self.ec2_client = ec2_client.EC2Client(
            self.cloud_auth, get_logger('ec2')
        )


class TestEC2ClientGetList(TestEC2Client):
    def setUp(self):
        TestEC2Client.setUp(self)

        self.fake_result = [
            {"fake": "reservation-1"},
            {"fake": "reservation-2"}
        ]
        self.ec2_conn.get_all_instances = mock.MagicMock(
            return_value=self.fake_result
        )

    def test_get_list(self):
        self.assertListEqual(self.ec2_client.get_list(), self.fake_result)
        self.ec2_conn.get_all_instances.assert_called_once_with()

    def test_error(self):
        self.ec2_conn.get_all_instances.side_effect = \
            boto_exception.EC2ResponseError(500, 'banana')
        self.assertIsNone(self.ec2_client.get_list())


class TestEC2ClientDestroy(TestEC2Client):
    def setUp(self):
        TestEC2Client.setUp(self)

        reservations = [
            mock.MagicMock(
                instances=[
                    mock.MagicMock(id='a', state='running'),
                    mock.MagicMock(id='b', state='terminated')
                ]
            ),
            mock.MagicMock(
                instances=[
                    mock.MagicMock(id='c', state='starting'),
                    mock.MagicMock(id='d', state='shutting-down')
                ]
            )
        ]
        self.ec2_conn.get_all_instances = mock.MagicMock(
            return_value=reservations
        )

        self.fake_result = [
            mock.MagicMock(
                instances=[mock.MagicMock(id='a', state='shutting-down')]
            ),
            mock.MagicMock(
                instances=[mock.MagicMock(id='c', state='shutting-down')]
            )
        ]
        self.ec2_conn.terminate_instances = mock.MagicMock(
            return_value=self.fake_result
        )

    def test_destroy_with_instance_ids(self):
        self.assertListEqual(
            self.ec2_client.destroy(['e', 'f']),
            self.fake_result
        )
        self.ec2_conn.terminate_instances.assert_called_once_with(['e', 'f'])

    def test_destroy_without_instance_ids(self):
        self.assertListEqual(
            self.ec2_client.destroy(),
            self.fake_result
        )
        self.ec2_conn.terminate_instances.assert_called_once_with(['a', 'c'])

    def test_destroy_with_no_instances(self):
        self.ec2_conn.get_all_instances = mock.MagicMock(return_value=[])
        self.assertListEqual(self.ec2_client.destroy(), [])
        self.ec2_conn.terminate_instance.assert_not_called()


class TestEC2ClientCreate(TestEC2Client):
    def setUp(self):
        TestEC2Client.setUp(self)

        self.fake_result = mock.MagicMock(id='r-123456')
        self.ec2_conn.run_instances = mock.MagicMock(
            return_value=self.fake_result
        )

    def test_create(self):
        spec = ec2_client.CfgEC2VMSpec(
            'm-123456',
            'key-1234567',
            flavor='m3.large',
            user_data='echo 123',
            security_group_id='sg-123456',
            subnet_id='sub-123456'
        )
        self.assertEqual(
            self.ec2_client.create(10, spec),
            self.fake_result
        )

        self.assertEqual(self.ec2_conn.run_instances.call_count, 1)
        self.ec2_conn.run_instances.assert_has_calls(
            [mock.call(
                spec.ami_id,
                instance_type=spec.flavor,
                key_name=spec.ssh_key_name,
                min_count=10,
                max_count=10,
                security_group_ids=[spec.security_group_id],
                subnet_id=spec.subnet_id,
                user_data=spec.user_data
            )]
        )

    def test_create_with_defaults(self):
        spec = ec2_client.CfgEC2VMSpec('m-123456', 'key-123456')
        self.assertEqual(
            self.ec2_client.create(10, spec),
            self.fake_result
        )

        self.assertEqual(self.ec2_conn.run_instances.call_count, 1)
        self.ec2_conn.run_instances.assert_has_calls(
            [mock.call(
                spec.ami_id,
                instance_type='t2.micro',
                key_name=spec.ssh_key_name,
                min_count=10,
                max_count=10
            )]
        )

    def test_error(self):
        spec = ec2_client.CfgEC2VMSpec('m-123456', 'key-123456')
        self.ec2_conn.run_instances.side_effect = \
            boto_exception.EC2ResponseError(500, 'banana')

        self.assertIsNone(self.ec2_client.create(2, spec))
