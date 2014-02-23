#import functools
import hashlib
import time

from pyramid.registry import global_registry


def get_task_id():
    timestamp = time.time()
    return hashlib.md5(str(timestamp)).hexdigest()


def task(func):

    def delay(*args, **kwargs):
        task_id = get_task_id()
        func = delay.func
        print func.func_name
        global_registry.producer.send_pyobj([
            task_id,
            func,
            args,
            kwargs
        ])
        return task_id

    func.delay = delay
    func.ready = False
    func.delay.func = func
    return func
