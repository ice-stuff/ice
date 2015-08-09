import unittest2
from ice import tasks
import fabric.api as fabric_api


def a_func(*args, **kwargs):
    """A help message"""
    ret_val = kwargs
    ret_val['args'] = args
    return ret_val


class TestCallable(unittest2.TestCase):
    def test_help_message(self):
        c = tasks.Callable(a_func)
        self.assertEqual(c.help_msg, 'A help message')

    def test_call(self):
        c = tasks.Callable(a_func)
        self.assertDictEqual(c(), {'args': tuple()})

    def test_call_with_args(self):
        c = tasks.Callable(a_func)
        self.assertDictEqual(c('banana', 12),
                             {'args': tuple(['banana', 12])})

    def test_call_with_kwargs(self):
        c = tasks.Callable(a_func)
        self.assertDictEqual(
            c(a_string='banana', a_int=12),
            {
                'a_string': 'banana',
                'a_int': 12,
                'args': tuple()
            }
        )

    def test_call_with_args_and_kwargs(self):
        c = tasks.Callable(a_func)
        self.assertDictEqual(
            c('hello_world', a_string='banana', a_int=12),
            {
                'a_string': 'banana',
                'a_int': 12,
                'args': tuple(['hello_world'])
            }
        )


def mock_decorator(func):
    def decorated_func(*args, **kwargs):
        ret_val = func(*args, **kwargs)
        ret_val['is_decorated'] = True
        return ret_val
    return decorated_func


class TestTask(unittest2.TestCase):
    def setUp(self):
        self.fa_task = fabric_api.task
        fabric_api.task = mock_decorator

    def tearDown(self):
        fabric_api.task = self.fa_task

    def test_callable_is_wrapped(self):
        c = tasks.Task(a_func)
        self.assertDictEqual(
            c('hello_world', a_int=12),
            {
                'a_int': 12,
                'args': tuple(['hello_world']),
                'is_decorated': True
            }
        )


class TestParallelTask(unittest2.TestCase):
    def setUp(self):
        self.fa_parallel = fabric_api.parallel
        fabric_api.parallel = mock_decorator

    def tearDown(self):
        fabric_api.parallel = self.fa_parallel

    def test_callable_is_wrapped(self):
        c = tasks.ParallelTask(a_func)
        self.assertDictEqual(
            c('hello_world', a_int=12),
            {
                'a_int': 12,
                'args': tuple(['hello_world']),
                'is_decorated': True
            }
        )
