import json
import requests
from requests import exceptions
import redo
import ice
from ice import entities

ICE_AGENT_URL = 'http://dl.bintray.com/glestaris/iCE/v2.1.0-rc.5/ice-agent'


class CfgRegistryClient(object):
    """Registry client configuration"""

    def __init__(self, host, port):
        """Creates a registry client configuration.

        :param str host: The address of the registry server.
        :param int port: The port of the registry server.
        """
        self.host = host
        self.port = port


class RegistryClient:
    VERSION = 'v2'

    class APIException(Exception):
        def __init__(self, **kwargs):
            self.http_code = kwargs.get('http_code', None)
            self.reason_msg = kwargs.get('reason_msg', None)
            self.response = kwargs.get('response', None)
            self.parent = kwargs.get('parent', None)

        def __str__(self):
            if self.http_code == 422:  # validation error
                iss_msgs = []
                for key, issue in self.response.json()['_issues'].items():
                    iss_msgs.append('`{:s}`: {:s}'.format(key, issue))
                return 'Validation error: ' + ', '.join(iss_msgs)
            else:
                return self._get_generic_str()

        def _get_generic_str(self):
            err_parts = []
            if self.http_code is not None:
                err_parts.append('HTTP error %d' % self.http_code)
            if self.reason_msg is not None:
                err_parts.append(self.reason_msg)
            if self.response is not None:
                try:
                    _dict = self.response.json()
                    err_parts.append(_dict['_error']['message'])
                except:
                    err_parts.append(self.response.text)
            if self.parent is not None:
                err_parts.append(str(self.parent))
            return ', '.join(err_parts)

    def __init__(self, cfg):
        self.cfg = cfg

    #
    # Getting IP address
    #

    def ping(self):
        """
        Pings the server.

        :rtype: bool
        :return: True if the server responds and False otherwise.
        """
        try:
            self._call('', return_raw=True)
            return True
        except RegistryClient.APIException:
            return False

    def ping_with_retries(self, attempts):
        retrier_kwargs = {
            'attempts': attempts,
            'sleeptime': 0.3,
            'jitter': 0
        }
        for _ in redo.retrier(**retrier_kwargs):
            if self.ping():
                return True

        return False

    def get_my_ip(self):
        """
        Gets the public IP address of the caller.

        :rtype: str
        :return: The IP address or `None` in case of failure.
        """
        return self._call('my_ip', return_raw=True)

    #
    # Session handling
    #

    def submit_session(self, session):
        """Submits session to API.

        :param entities.Session session: The session to store.
        :rtype: str
        :return: The id of the created session.
        """
        resp = self._call('sessions', 'POST', data=session.to_dict())
        session.id = resp['_id']
        return session.id

    def delete_session(self, session):
        """Deletes a specific session.

        :param ice.entities.Session session: The session.
        :rtype: bool
        :return: `True` on success and `False` otherwise.
        """
        if session is None:
            return False

        instances = self.get_instances_list(session)
        for inst in instances:
            self.delete_instance(inst)

        try:
            resp = self._call('sessions/%s' % session.id, 'DELETE')
            if resp is None:
                return False
            return True
        except RegistryClient.APIException:
            return False

    def get_sessions_list(self):
        """Gets list of active sessions.

        :rtype: list of [entities.Session]
        :return: List of session objects.
        """
        ret_val = []

        resp = self._call('sessions', 'GET')
        for entry in resp['_items']:
            ret_val.append(entities.Session(**entry))

        return ret_val

    def get_session(self, session_id):
        """Gets a session given its id.

        :param str session_id: The session id.
        :rtype: entities.Session|None
        :return: The requested session or `None` if not found.
        """
        try:
            resp = self._call('sessions/%s' % session_id, 'GET')
            if resp is None:
                return None
            return entities.Session(**resp)
        except RegistryClient.APIException:
            return None

    #
    # Instance handling
    #

    def submit_instance(self, inst):
        """
        Submits a new instance.

        :param entities.Instance inst: The instance
        :rtype: str
        :return: The instance id on success and `None` on failure.
        """
        resp = self._call('instances', 'POST', data=inst.to_dict())
        inst.id = resp['_id']
        return inst.id

    def delete_instance(self, inst):
        """
        Deletes an instance from the backend.

        :param entities.Instance inst: The instance
        :rtype: bool
        :return: `True` on success and `False` otherwise.
        """
        self._call('instances/%s' % inst.id, 'DELETE')

    def get_instances_list(self, session=None):
        """
        Returns a list of instances.

        :param ice.entities.Session session: The session.
        :rtype: list of [entities.Instance]
        :return: List of `entities.Instance` instances.
        """
        params = None
        if session is not None:
            params = {
                'where': '{"session_id": "%s"}' % session.id
            }

        resp = self._call('instances', 'GET', params=params)
        ret_val = []
        for entry in resp['_items']:
            ret_val.append(entities.Instance(**entry))

        return ret_val

    def get_instance(self, inst_id):
        """
        Returns an instance given its id.

        :param str inst_id: The id of the instance.
        :rtype: entities.Instance
        :return: An instance or `None` in case of error.
        """
        try:
            resp = self._call('instances/%s' % inst_id, 'GET')
            if resp is None:
                return None
            return entities.Instance(**resp)
        except RegistryClient.APIException:
            return None

    #
    # User data for ice-agent
    #

    # TODO: consider splitting this method out of RegistryClient class.
    def compile_user_data(self, sess, cfg, **tags):
        """Compiles the user-data string for new VMs.

        :param ice.entities.Session sess: Active iCE session.
        :param ice.registry.client.CfgRegistryClient cfg: iCE client config.
        :param string tags: Any keyword argument, not mentioned here, will be
            considered a tag.
        :rtype: str
        :return: Base64 encoded user data.
        """
        user_data = """#!/bin/sh -ex
wget {:s} -O ./ice-agent
chmod +x ./ice-agent
""".format(ICE_AGENT_URL)
        user_data += './ice-agent register-self' + \
            ' --api-endpoint http://{:s}:{:d}'.format(cfg.host, cfg.port) + \
            ' --session-id {:s}'.format(sess.id)
        for key, value in tags.items():
            user_data += ' --tag {:s}={:s}'.format(key, value)
        user_data += '\n'

        return user_data

    #
    # Helpers
    #

    def _get_url(self, suffix):
        """
        Compiles the full URL of the resource.

        :param str suffix: The URL suffix (without leading /).
        :rtype: str
        :return: The full URL.
        """
        if self.cfg.port == 443:
            url = 'https://'
        else:
            url = 'http://'
        url += self.cfg.host
        if self.cfg.port != 80 and self.cfg.port != 443:
            url += ':%d' % self.cfg.port
        url += '/%s/%s' % (self.VERSION, suffix)
        return url

    def _call(self, url_suffix, method='GET', params=None, data=None,
              return_raw=False):
        """
        Performs a request to the API.

        :param str url_suffix: The URL suffix (without leading /).
        :param str method: An HTTP verb.
        :param dict params: URL parameters.
        :param dict data: The data dictionary.
        :param bool return_raw: If set, response will be a string.
        :rtype: dict|str
        :return: The response dictionary or the response string if `return_raw`
            is set.
        :raises RegistryClient.APIException: In case of error.
        """
        # Find the method
        try:
            method = getattr(requests, method.lower())
        except AttributeError:
            # Unknown HTTP verb
            return None

        # Build the keyword arguments of the method
        args = {
            'headers': {
                'User-Agent': 'iCE Client/%s' % ice.__version__
            }
        }
        if data is not None:
            args['headers']['Content-Type'] = 'application/json'
            args['data'] = json.dumps(data)
        if params is not None:
            args['params'] = params

        # Run the method
        try:
            resp = method(self._get_url(url_suffix), **args)
        except exceptions.RequestException as err:
            raise RegistryClient.APIException(parent=err)
        if resp.status_code / 100 != 2:
            raise RegistryClient.APIException(
                http_code=resp.status_code,
                response=resp
            )

        # Parse response
        if return_raw:
            return resp.text
        if resp.text == '':
            return ''
        try:
            return resp.json()
        except ValueError as err:
            raise RegistryClient.APIException(parent=err)
