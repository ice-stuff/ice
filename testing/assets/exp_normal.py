from ice import tasks


@tasks.Runner
def run_a(hosts):
    pass


@tasks.Task
def task_a_a(hosts):
    pass


@tasks.Task
def task_a_b(hosts):
    """Hello world"""
    pass


@tasks.Runner
def run_b(hosts):
    """I am a fast runner"""
    pass


@tasks.Task
def task_b_a(hosts):
    pass


@tasks.Task
def task_b_b(hosts):
    """A helpful message"""
    pass


@tasks.Task
def task_b_c(hosts):
    pass


def a_func():
    pass
