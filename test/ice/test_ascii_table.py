import unittest2
from ice import ascii_table


class TestASCIITable(unittest2.TestCase):
    def test_add_column(self):
        t = ascii_table.ASCIITable(80)
        col = ascii_table.ASCIITableColumn("Test", 20)
        t.add_column('test', col)
        self.assertEqual(t.cols, {"test": col})

    def test_add_column_with_unknown_type(self):
        t = ascii_table.ASCIITable(80)
        with self.assertRaises(TypeError):
            t.add_column('test', {"hello": "world"})

    def test_add_row(self):
        t = ascii_table.ASCIITable(80)
        col = ascii_table.ASCIITableColumn("Test", 20)
        t.add_column('test', col)

        row = {
            'test': 'hello-world'
        }
        t.add_row(row)

        self.assertEqual(t.rows, [row])

    def test_add_row_with_missing_field(self):
        t = ascii_table.ASCIITable(80)
        col = ascii_table.ASCIITableColumn("Test", 20)
        t.add_column('test', col)

        row = {}
        with self.assertRaises(ValueError):
            t.add_row(row)
        self.assertListEqual(t.rows, [])

    def test_add_row_with_non_existing_field(self):
        t = ascii_table.ASCIITable(80)

        row = {
            'non_existing_key': 'hello world'
        }
        with self.assertRaises(ValueError):
            t.add_row(row)
        self.assertListEqual(t.rows, [])
