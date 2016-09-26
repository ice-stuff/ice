import unittest2
from ice import entities
from ice.registry import client


class TestCompileUserData(unittest2.TestCase):
    def test(self):
        # client will not try to connect to the endpoint
        c = client.RegistryClient('localhost', 8080)

        user_data = c.compile_user_data(
            entities.Session(
                _id='1234abcd',
                client_ip_addr='80.10.100.200'
            ),
            client.CfgRegistryClient('public.ice.registry', 1234)
        )
        self.assertEquals(
            user_data,
            """#!/bin/bash
curl {:s} -O ./ice-register-self.py
chmod +x ./ice-register-self.py
./ice-register-self.py -a http://public.ice.registry:1234 -s 1234abcd
""".format(client.ICE_REGISTRATION_SCRIPT_URL)
        )
