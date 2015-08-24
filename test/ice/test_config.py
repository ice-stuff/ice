import unittest2
import ConfigParser

from ice import ec2_client
from ice import config
import ice.registry.server as reg_server
import ice.registry.client as reg_client


class TestConfigFactory(unittest2.TestCase):
    def setUp(self):
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.add_section('registry_server')
        self.cfg.add_section('mongodb')
        self.cfg.add_section('shell')
        self.cfg.add_section('registry_client')
        self.cfg.add_section('ec2')

        self.config_factory = config.ConfigFactory(self.cfg)

        self.addTypeEqualityFunc(ec2_client.CfgEC2CloudAuth,
                                 self.assertObjectEqual)
        self.addTypeEqualityFunc(ec2_client.CfgEC2VMSpec,
                                 self.assertObjectEqual)
        self.addTypeEqualityFunc(reg_client.CfgRegistryClient,
                                 self.assertObjectEqual)
        self.addTypeEqualityFunc(reg_server.CfgRegistryServer,
                                 self.assertObjectEqual)

    def assertObjectEqual(self, a, b, **kwargs):
        self.assertIsInstance(b, a.__class__, **kwargs)
        self.assertDictEqual(a.__dict__, b.__dict__, **kwargs)


class TestGetEc2CloudIds(TestConfigFactory):
    def test(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')

        self.assertListEqual(
            self.config_factory.get_ec2_cloud_ids(),
            ['aws-1', 'aws-2']
        )


class TestGetEc2Auth(TestConfigFactory):
    def test(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'region', 'aws-1')
        self.cfg.set('ec2_aws-1', 'aws_access_key', 'AnAccesssKey123')
        self.cfg.set('ec2_aws-1', 'aws_secret_key', 'ASecretKey')

        self.assertEqual(
            self.config_factory.get_ec2_cloud_auth('aws-1'),
            ec2_client.CfgEC2CloudAuth(
                'aws-1',
                'AnAccesssKey123',
                'ASecretKey'
            )
        )

    def test_w_url(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'url', 'aws-1.aws.amazon.com')
        self.cfg.set('ec2_aws-1', 'aws_access_key', 'AnAccesssKey123')
        self.cfg.set('ec2_aws-1', 'aws_secret_key', 'ASecretKey')

        self.assertEqual(
            self.config_factory.get_ec2_cloud_auth('aws-1'),
            ec2_client.CfgEC2CloudAuth(
                'aws-1.aws.amazon.com',
                'AnAccesssKey123',
                'ASecretKey'
            )
        )

    def test_missing_url(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'aws_access_key', 'AnAccesssKey123')
        self.cfg.set('ec2_aws-1', 'aws_secret_key', 'ASecretKey')

        with self.assertRaises(config.ConfigFactory.OptionNotFound):
            self.config_factory.get_ec2_cloud_auth('aws-1')

    def test_missing_access_key(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'region', 'aws-1')
        self.cfg.set('ec2_aws-1', 'aws_secret_key', 'ASecretKey')

        with self.assertRaises(config.ConfigFactory.OptionNotFound):
            self.config_factory.get_ec2_cloud_auth('aws-1')

    def test_missing_secret_key(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'region', 'aws-1')
        self.cfg.set('ec2_aws-1', 'aws_access_key', 'AnAccesssKey123')

        with self.assertRaises(config.ConfigFactory.OptionNotFound):
            self.config_factory.get_ec2_cloud_auth('aws-1')


class TestGetEc2VMSpec(TestConfigFactory):
    def test(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'default_ami_id', 'ami-123456')
        self.cfg.set('ec2_aws-1', 'default_flavor', 'm3.medium')
        self.cfg.set('ec2_aws-1', 'ssh_key_name', 'test-ice')
        self.cfg.set('ec2_aws-1', 'security_group_id', 'sg-123456')
        self.cfg.set('ec2_aws-1', 'subnet_id', 'sn-123')

        self.assertEqual(
            self.config_factory.get_ec2_vm_spec('aws-1'),
            ec2_client.CfgEC2VMSpec(
                'ami-123456',
                'test-ice',
                flavor='m3.medium',
                security_group_id='sg-123456',
                subnet_id='sn-123'
            )
        )

    def test_missing_ami(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'ssh_key_name', 'test-ice')

        with self.assertRaises(config.ConfigFactory.OptionNotFound):
            self.config_factory.get_ec2_vm_spec('aws-1')

    def test_missing_ssh_key(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'default_ami_id', 'ami-123456')

        with self.assertRaises(config.ConfigFactory.OptionNotFound):
            self.config_factory.get_ec2_vm_spec('aws-1')

    def test_wo_flavor(self):
        self.cfg.set('ec2', 'clouds', 'aws-1,aws-2')
        self.cfg.set('ec2', 'default_flavor', 'm3.medium')
        self.cfg.add_section('ec2_aws-1')
        self.cfg.set('ec2_aws-1', 'default_ami_id', 'ami-123456')
        self.cfg.set('ec2_aws-1', 'ssh_key_name', 'test-ice')

        self.assertEqual(
            self.config_factory.get_ec2_vm_spec('aws-1'),
            ec2_client.CfgEC2VMSpec(
                'ami-123456',
                'test-ice',
                flavor='m3.medium'
            )
        )


class TestGetRegstryClient(TestConfigFactory):
    def test_defaults(self):
        self.assertEqual(
            self.config_factory.get_registry_client(),
            reg_client.CfgRegistryClient(
                host='localhost', port=5000
            )
        )


    def test_all_provided(self):
        self.cfg.set('registry_client', 'host', '192.168.1.1')
        self.cfg.set('registry_client', 'port', '8081')

        self.assertEqual(
            self.config_factory.get_registry_client(),
            reg_client.CfgRegistryClient(
                host='192.168.1.1', port=8081
            )
        )


class TestGetRegstryServer(TestConfigFactory):
    def test_defaults(self):
        self.cfg.set('mongodb', 'db_name', 'db-12')

        self.assertEqual(
            self.config_factory.get_registry_server(),
            reg_server.CfgRegistryServer(
                debug=False,
                host='localhost', port=5000,
                mongo_host='localhost', mongo_port=27017,
                mongo_user='', mongo_pass='',
                mongo_db='db-12'
            )
        )

    def test_required(self):
        with self.assertRaises(config.ConfigFactory.OptionNotFound):
            self.config_factory.get_registry_server()

    def test_all_provided(self):
        self.cfg.set('registry_server', 'debug', '1')
        self.cfg.set('registry_server', 'host', '192.168.1.1')
        self.cfg.set('registry_server', 'port', '8081')
        self.cfg.set('mongodb', 'host', 'node-12.mongoasaservice.com')
        self.cfg.set('mongodb', 'port', '121212')
        self.cfg.set('mongodb', 'username', 'user-12')
        self.cfg.set('mongodb', 'password', 'password-12')
        self.cfg.set('mongodb', 'db_name', 'db-12')

        self.assertEqual(
            self.config_factory.get_registry_server(),
            reg_server.CfgRegistryServer(
                debug=True,
                host='192.168.1.1', port=8081,
                mongo_host='node-12.mongoasaservice.com', mongo_port=121212,
                mongo_user='user-12', mongo_pass='password-12',
                mongo_db='db-12'
            )
        )
