import unittest2
from ice import ascii_table


class TestASCIITable(unittest2.TestCase):
    def test_add_column(self):
        t = ascii_table.ASCIITable()
        col = ascii_table.ASCIITableColumn('Test', 20)
        t.add_column('test', col)
        self.assertEqual(t.cols, [col])

    def test_add_column_with_unknown_type(self):
        t = ascii_table.ASCIITable()
        with self.assertRaises(TypeError):
            t.add_column('test', {'hello': 'world'})

    def test_add_column_after_rows_has_been_added(self):
        t = ascii_table.ASCIITable()
        col = ascii_table.ASCIITableColumn('Test', 20)
        t.add_column('test', col)

        row = {
            'test': 'hello-world'
        }
        t.add_row(row)

        with self.assertRaises(StandardError):
            col = ascii_table.ASCIITableColumn('Another column', 20)
            t.add_column('another_col', col)

    def test_add_row(self):
        t = ascii_table.ASCIITable()
        col = ascii_table.ASCIITableColumn('Test', 20)
        t.add_column('test', col)

        row = {
            'test': 'hello-world'
        }
        t.add_row(row)

        self.assertEqual(len(t.rows), 1)
        self.assertIsInstance(t.rows[0], ascii_table.ASCIITableRow)
        self.assertEqual(t.rows[0].dict, row)

    def test_add_comment_row(self):
        t = ascii_table.ASCIITable()
        col = ascii_table.ASCIITableColumn('Test', 20)
        t.add_column('test', col)

        t.add_row({'test': 'hello-world'})
        t.add_comment_row('hello world')

        self.assertEqual(len(t.rows), 2)
        self.assertIsInstance(t.rows[0], ascii_table.ASCIITableRow)
        self.assertIsInstance(t.rows[1], ascii_table.ASCIITableRowComment)
        self.assertEqual(t.rows[1].text, 'hello world')

    def test_add_row_with_missing_field(self):
        t = ascii_table.ASCIITable()
        col = ascii_table.ASCIITableColumn('Test', 20)
        t.add_column('test', col)

        row = {}
        with self.assertRaises(ValueError):
            t.add_row(row)
        self.assertListEqual(t.rows, [])

    def test_add_row_with_non_existing_field(self):
        t = ascii_table.ASCIITable()

        row = {
            'non_existing_key': 'hello world'
        }
        with self.assertRaises(ValueError):
            t.add_row(row)
        self.assertListEqual(t.rows, [])


class TestASCIIRenderer(unittest2.TestCase):
    def test_renders(self):
        table = ascii_table.ASCIITable()
        table.add_column('col_a', ascii_table.ASCIITableColumn('Column A', 30))
        table.add_column('col_b', ascii_table.ASCIITableColumn('Column B', 15))
        table.add_column('col_c', ascii_table.ASCIITableColumn('Column C', 20))
        table.add_row({
            'col_a': 'hello world #1',
            'col_b': 'foo bar #1',
            'col_c': 'another test #1',
        })
        table.add_row({
            'col_a': 'foo bar #2',
            'col_b': 'hello #2',
            'col_c': 'another test #2',
        })
        table.add_row({
            'col_a': 'another test #3',
            'col_b': 'foo bar #3',
            'col_c': 'hello world #3',
        })
        table.add_row({
            'col_a': 'hello world #4',
            'col_b': 'another #4',
            'col_c': 'foo bar #4',
        })

        renderer = ascii_table.ASCIITableRenderer()
        self.maxDiff = 2500
        self.assertEqual(
            renderer.render(table),
            """-----------------------------------------------------------------
| Column A                    | Column B     | Column C         |
-----------------------------------------------------------------
| hello world #1              | foo bar #1   | another test #1  |
| foo bar #2                  | hello #2     | another test #2  |
| another test #3             | foo bar #3   | hello world #3   |
| hello world #4              | another #4   | foo bar #4       |
-----------------------------------------------------------------
""")

    def test_renders_when_val_is_larger_than_width(self):
        table = ascii_table.ASCIITable()
        table.add_column('col_a', ascii_table.ASCIITableColumn('Column A', 30))
        table.add_column('col_b', ascii_table.ASCIITableColumn('Column B', 15))
        table.add_row({
            'col_a': 'hello world #1',
            'col_b': 'foo bar #1',
        })
        table.add_row({
            'col_a': 'foo bar #2',
            'col_b': 'hello world #2',
        })

        renderer = ascii_table.ASCIITableRenderer()
        self.maxDiff = 2500
        self.assertEqual(
            renderer.render(table),
            """---------------------------------------------
| Column A                    | Column B    |
---------------------------------------------
| hello world #1              | foo bar #1  |
| foo bar #2                  | hello world |
---------------------------------------------
""")

    def test_renders_when_val_is_none(self):
        table = ascii_table.ASCIITable()
        table.add_column('col_a', ascii_table.ASCIITableColumn('Column A', 30))
        table.add_column('col_b', ascii_table.ASCIITableColumn('Column B', 15))
        table.add_row({
            'col_a': 'hello world #1',
            'col_b': None,
        })

        renderer = ascii_table.ASCIITableRenderer()
        self.maxDiff = 2500
        self.assertEqual(
            renderer.render(table),
            """---------------------------------------------
| Column A                    | Column B    |
---------------------------------------------
| hello world #1              |             |
---------------------------------------------
""")

    def test_renders_when_comment_row_is_provided(self):
        table = ascii_table.ASCIITable()
        table.add_column('col_a', ascii_table.ASCIITableColumn('Column A', 30))
        table.add_column('col_b', ascii_table.ASCIITableColumn('Column B', 15))
        table.add_row({
            'col_a': 'hello #1',
            'col_b': 'foo #1',
        })
        table.add_comment_row('hello world')
        table.add_row({
            'col_a': 'foo #2',
            'col_b': 'hello #2',
        })

        renderer = ascii_table.ASCIITableRenderer()
        self.maxDiff = 2500
        self.assertEqual(
            renderer.render(table),
            """---------------------------------------------
| Column A                    | Column B    |
---------------------------------------------
| hello #1                    | foo #1      |
| ----------------------------------------- |
| hello world                               |
| ----------------------------------------- |
| foo #2                      | hello #2    |
---------------------------------------------
""")
