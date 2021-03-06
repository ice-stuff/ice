"""ASCII table generator"""


class ASCIITableRenderer(object):
    def render(self, table):
        total_width = 0
        for col in table.cols:
            total_width += col.width

        # Header
        out = self._format_separator(total_width)
        cols_widths = [col.width for col in table.cols]
        out += self._format_row([col.label for col in table.cols], cols_widths)
        out += self._format_separator(total_width)

        # Body
        for row in table.rows:
            if isinstance(row, ASCIITableRowComment):
                out += self._format_row_comment(row.text, total_width)
            else:
                out += self._format_row(
                    [row.dict[key] for key in table.col_keys],
                    cols_widths
                )

        # Footer
        out += self._format_separator(total_width)

        return out

    def _format_separator(self, width):
        return '-' * width + '\n'

    def _format_row_comment(self, text, width):
        actual_width = width-4

        out = ''
        out += '| ' + ('-' * actual_width) + ' |\n'
        form_str = '| {:' + '{:d}'.format(actual_width) + '} |\n'
        out += form_str.format(text)
        out += '| ' + ('-' * actual_width) + ' |\n'

        return out

    def _format_row(self, values, widths):
        out = ''
        for i, width in enumerate(widths):
            actual_width = width - 3
            # last column loses one more space for the trailing `|`
            if i == len(widths) - 1:
                actual_width -= 1

            val = self._trunc(values[i], actual_width)
            form_str = '| {:' + '{:d}'.format(actual_width) + 's} '
            out += form_str.format(val)
        out += '|\n'

        return out

    def _trunc(self, contents, width):
        if contents is None:
            return ''
        if len(contents) <= width:
            return contents
        return contents[:width]


class ASCIITableColumn(object):
    def __init__(self, label, width):
        self.label = label
        self.width = width


class ASCIITableRow(object):
    def __init__(self, dict):
        self.dict = dict


class ASCIITableRowComment(ASCIITableRow):
    def __init__(self, text):
        ASCIITableRow.__init__(self, {})
        self.text = text


class ASCIITable(object):
    def __init__(self):
        # list of strings
        self.col_keys = []
        # list of ASCIITableColumn
        self.cols = []
        # list of ASCIITableRow
        self.rows = []

    def add_column(self, key, col):
        if len(self.rows) != 0:
            raise StandardError(
                'cannot add columns after rows have been added'
            )
        if not isinstance(col, ASCIITableColumn):
            raise TypeError()
        self.col_keys.append(key)
        self.cols.append(col)

    def add_comment_row(self, text):
        row = ASCIITableRowComment(text)
        self.rows.append(row)

    def add_row(self, dict):
        dict_keys = dict.keys()
        expected_keys = self.col_keys
        if set(dict_keys) != set(expected_keys):
            self._find_missing_key(expected_keys, dict_keys)
            self._find_unknown_key(expected_keys, dict_keys)

        row = ASCIITableRow(dict)
        self.rows.append(row)

    def _find_missing_key(self, expected_keys, row_keys):
        for expected_key in expected_keys:
            if expected_key in row_keys:
                continue
            raise ValueError('key `{}` is missing'.format(expected_key))

    def _find_unknown_key(self, expected_keys, row_keys):
        for row_key in row_keys:
            if row_key in expected_keys:
                continue
            raise ValueError('key `{}` is not defined'.format(row_key))
