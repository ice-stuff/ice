import json

import requests
from requests import exceptions

import ice
from ice import entities


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
    VERSION = 'v1'

    class APIException(Exception):

        def __init__(self, **kwargs):
            self.http_code = kwargs.get('http_code', None)
            self.reason_msg = kwargs.get('reason_msg', None)
            self.response = kwargs.get('response', None)
            self.parent = kwargs.get('parent', None)

        def __str__(self):
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

    def __init__(self, hostname='localhost', port=5000):
        self.hostname = hostname
        self.port = port

    #
    # Getting IP address
    #

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

    def delete_session(self, session_id):
        """Deletes a specific session.

        :param str session_id: The session id.
        :rtype: bool
        :return: `True` on success and `False` otherwise.
        """
        # Delete linked instances
        #   TODO: I cannot figure out why commented-out code does not work. It
        #       deletes all the instances (of all the sessions)!
        instances = self.get_instances_list(session_id)
        for inst in instances:
            self.delete_instance(inst)
        # params = {
        #     'where': '{"session_id": "%s"}' % session_id
        # }
        # resp = self._call('instances', 'DELETE', params=params)

        # Delete session
        try:
            resp = self._call('sessions/%s' % session_id, 'DELETE')
            if resp is None:
                return False
            return True
        except APIClient.APIException:
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
        except APIClient.APIException:
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

    def delete_instance(self, inst_id):
        """
        Deletes an instance from the backend.

        :param str inst_id: The id of the instance.
        :rtype: bool
        :return: `True` on success and `False` otherwise.
        """
        try:
            resp = self._call('instances/%s' % inst_id, 'DELETE')
            return (resp is not None)
        except APIClient.APIException:
            return False

    def get_instances_list(self, session_id=None):
        """
        Returns a list of instances.

        :param str session_id: The session id.
        :rtype: list of [entities.Instance]
        :return: List of `entities.Instance` instances.
        """
        # Make calls
        params = None
        if session_id is not None:
            params = {
                'where': '{"session_id": "%s"}' % session_id
            }
        resp = self._call('instances', 'GET', params=params)

        # Process results
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
        except APIClient.APIException:
            return None

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
        if self.port == 443:
            url = 'https://'
        else:
            url = 'http://'
        url += self.hostname
        if self.port != 80 and self.port != 443:
            url += ':%d' % self.port
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
        :raises APIClient.APIException: In case of error.
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
            raise APIClient.APIException(parent=err)
        if resp.status_code / 100 != 2:
            raise APIClient.APIException(
                http_code=resp.status_code,
                response=resp
            )

        # Parse response
        if return_raw:
            return resp.text
        try:
            resp_parsed = resp.json()
        except ValueError as err:
            # Raise parse exception
            raise APIClient.APIException(parent=err)

        return resp_parsed
