import json
import requests
from requests.exceptions import RequestException
from .entities import Instance

___version__ = '0.0.1'


class APIClient:
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
    # Instance handling
    #

    def submit_instance(self, inst):
        """
        Submits a new instance.

        :param entities.Instance inst: The instance
        :rtype: str
        :return: The instance id on success and `None` on failure.
        """
        resp = self._call('instances', 'POST', inst.to_dict())
        inst.id = resp['_id']
        return inst.id

    def delete_instance(self, instId):
        """
        Deletes an instance from the backend.

        :param str instId: The id of the instance.
        :rtype: bool
        :return: `True` on success and `False` otherwise.
        """
        resp = self._call('instances/%s' % instId, 'DELETE')
        return (resp is not None)

    def get_instances_list(self):
        """
        Returns a list of instances.

        :rtype: list
        :return: List of `entites.Instance` instances.
        """
        ret_val = []

        resp = self._call('instances', 'GET')
        for entry in resp['_items']:
            ret_val.append(Instance(**entry))

        return ret_val

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

    def _call(self, url_suffix, method='GET', data=None, return_raw=False):
        """
        Performs a request to the API.

        :param str url_suffix: The URL suffix (without leading /).
        :param str method: An HTTP verb.
        :param dict data: The data dictionary.
        :param bool return_raw: If set, response will be a string.
        :rtype: dict|str
        :return: The response dictionary or the response string if `return_raw`
            is set.
        :raises APIClient.APIException: In case of error.
        """
        # Find the method
        method = getattr(requests, method.lower())
        if method is None:
            # Unknown HTTP verb
            return None

        # Make the request
        args = {
            'headers': {
                'User-Agent': 'iCE Client/%s' % ___version__
            }
        }
        if data is not None:
            args['headers']['Content-Type'] = 'application/json'
            args['data'] = json.dumps(data)

        # Run the request
        try:
            resp = method(self._get_url(url_suffix), **args)
        except RequestException as err:
            raise APIClient.APIException(err)
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
            raise APIClient.APIException(err)

        return resp_parsed
