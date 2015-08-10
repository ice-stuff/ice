import unittest2
import mock
from ice import ec2_client
from boto import ec2 as boto_ec2


class TestEC2CloudAuth(unittest2.TestCase):
    def setUp(self):
        self.ec2_ctr = boto_ec2.connect_to_region
        boto_ec2.connect_to_region = mock.MagicMock()
        boto_ec2.connect_to_region.return_value = object()

        self.cloud_auth = ec2_client.EC2CloudAuth(
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
