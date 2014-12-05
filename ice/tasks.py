"""Fabric - iCE tasks."""
from fabric import api


class Callable(object):
    def __init__(self, func):
        self.func = func
        self.help_msg = func.__doc__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Runner(Callable):
    pass


class Task(Callable):
    def __init__(self, func):
        super(Task, self).__init__(func)
        self.func = api.task(func)


class ParallelTask(Task):
    def __init__(self, func):
        super(ParallelTask, self).__init__(func)
        self.func = api.parallel(func)
