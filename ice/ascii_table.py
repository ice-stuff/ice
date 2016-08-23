"""ASCII table generator"""


class ASCIITableColumn(object):
    def __init__(self, label, width):
        self.label = label
        self.width = width


class ASCIITable(object):
    def __init__(self, width):
        # dict of key => ASCIITableColumn
        self.cols = {}
        # list of dicts
        self.rows = []

    def add_column(self, key, col):
        if not isinstance(col, ASCIITableColumn):
            raise TypeError()
        self.cols[key] = col

    def add_row(self, row):
        row_keys = row.keys()
        expected_keys = self.cols.keys()
        if set(row_keys) != set(expected_keys):
            self._find_missing_key(expected_keys, row_keys)
            self._find_unknown_key(expected_keys, row_keys)

        self.rows.append(row)

    def _find_missing_key(self, expected_keys, row_keys):
        for expected_key in expected_keys:
            if expected_keys in row_keys:
                continue
            raise ValueError('key `{}` is missing'.format(expected_key))

    def _find_unknown_key(self, expected_keys, row_keys):
        for row_key in row_keys:
            if row_key in expected_keys:
                continue
            raise ValueError('key `{}` is not defined'.format(row_key))
