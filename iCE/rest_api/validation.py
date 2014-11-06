import re
from cerberus import Validator
from cerberus.errors import ERROR_BAD_TYPE


class MyValidator(Validator):

    def __init__(self, *args, **kwargs):
        Validator.__init__(self, *args, **kwargs)

        # RegExs
        self._ip_re = None

    def _validate_type_ip(self, field, value):
        """ Enables validation for `ip` schema attribute.

        :param unique: Boolean, whether the field value should be
                       unique or not.
        :param field: field name.
        :param value: field value.
        """
        if self._ip_re is None:
            self._ip_re = re.compile(
                r'^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$'
            )

        # Run regular expression
        m = re.match(self._ip_re, value)

        # Check general format
        if m is None:
            self._error(field, ERROR_BAD_TYPE % 'Ip')
            return

        # Check parts
        for i in range(1, 4):
            part = int(m.group(i))
            if part <= 0 or part > 255:
                self._error(field, ERROR_BAD_TYPE % 'Ip')

    def _validate_type_url(self, field, value):
        """ Enables validation for `url` schema attribute.

        :param unique: Boolean, whether the field value should be
                       unique or not.
        :param field: field name.
        :param value: field value.
        """
        pass
