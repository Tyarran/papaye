class TaskRegistry(object):
    _shared_state = {}
    _tasks = {}

    def __init__(self):
        self.__dict__ = self._shared_state

    def register_task(self, func):
        self._tasks[func.__name__] = func

    def register_scheduler(self, scheduler):
        self._scheduler = scheduler


class Task(object):

    def __init__(self, func):
        self.func = func

    def delay(self, *args, **kwargs):
        scheduler = TaskRegistry()._scheduler
        scheduler.add_task(self.func, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

    def __repr__(self):
        return '<{}.{} for "{}" function>'.format(self.__module__, self.__class__.__name__, self.func.__name__)


def task(func):
    task = Task(func)
    registry = TaskRegistry()
    registry.register_task(func)
    return task
