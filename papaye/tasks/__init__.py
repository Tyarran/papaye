#import functools
import hashlib
import time

from pyramid.registry import global_registry


class TaskRegistry(object):
    _shared_state = {}
    _tasks = {}

    def __init__(self):
        self.__init__ = self._shared_state

    def register_task(self, func):
        self._tasks[func.__name__] = func


class Task(object):

    def __init__(self, func):
        self.func = func

    def get_task_id(self):
        timestamp = time.time()
        return hashlib.md5(str(timestamp)).hexdigest()

    def delay(self, *args, **kwargs):
        self.task_id = self.get_task_id()
        global_registry.producer.send_pyobj([
            self.task_id,
            self.func.func_name,
            args,
            kwargs
        ])
        return self.task_id

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

    @property
    def ready(self):
        cache = global_registry.result_cache
        return self.task_id in cache

    @property
    def result(self):
        cache = global_registry.result_cache
        return cache.get_value(self.task_id)

    def __repr__(self):
        return '<{}.{} for "{}"" function>'.format(self.__module__, self.__class__.__name__, self.func.func_name)


def task(func):
    task = Task(func)
    registry = TaskRegistry()
    registry.register_task(func)
    return task
