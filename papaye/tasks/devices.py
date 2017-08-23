import collections
import datetime
import itertools
import logging
import queue
import signal
import sys
import threading
import time

from termcolor import colored


COLORS_GEN = itertools.cycle((
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
    'grey',
    'red',
))
STATUS_NAMES = ('PENDING', 'WIP', 'DONE', 'ERROR')
STATUS_TYPE = collections.namedtuple('Status', STATUS_NAMES)
STATUS = STATUS_TYPE(**dict((name, value) for name, value in zip(
    STATUS_NAMES, range(0, len(STATUS_NAMES))))
)
LOGGER = logging.getLogger(__name__)


class IScheduler(object):
    status = None
    queue = None
    results = None

    def start(self):
        raise NotImplemented()

    def add_task(self):
        raise NotImplemented()

    def task_id(self, task_tuple):
        raise NotImplemented()

    def get_task(self):
        raise NotImplemented()

    def add_result(self, *args, **kwargs):
        raise NotImplemented()

    def status(self, task_id):
        raise NotImplemented()

    def shutdown(self):
        raise NotImplemented()


class DummyScheduler(object):

    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def add_task(self, *args):
        pass

    def task_id(self, task_tuple):
        pass

    def get_task(self):
        pass

    def add_result(self, *args, **kwargs):
        pass

    def status(self, task_id):
        pass

    def shutdown(self):
        pass


class MultiThreadScheduler(IScheduler):

    def __init__(self, workers=1):
        self.workers = int(workers)
        self.queue = queue.Queue()
        self.results = {}
        self.counter = itertools.count(1)
        self.status_history = {}
        self.worker_list = []
        signal.signal(signal.SIGTERM, self.shutdown)

    def start(self):
        logging.info('Start {} scheduler with {} workers'.format(
            self.__class__.__name__, self.workers)
        )
        for index in range(1, self.workers + 1):
            worker = ThreadWorker(index, self)
            worker.daemon = True
            worker.start()
            self.worker_list.append(worker)

    def add_task(self, func, *args, **kwargs):
        task_id = self.task_id(None)
        self.queue.put((task_id, func, args, kwargs))
        self.results[task_id] = {
            "status": STATUS.PENDING,
            "result": None
        }
        if task_id not in self.status_history:
            self.status_history[task_id] = []
        self.status_history[task_id].append(
            (STATUS.PENDING, datetime.datetime.now())
        )

    def task_id(self, task_tuple):
        return next(self.counter)

    def get_task(self):
        if self.queue.qsize() == 0:
            return None
        return self.queue.get()

    def add_result(self, task_id, worker_id, result):
        self.results[task_id] = (worker_id, result)
        self.status_history[task_id].append(
            (STATUS.DONE, datetime.datetime.now())
        )

    def status(self, task_id):
        return self.results[task_id]

    def shutdown(self, signum, frame):
        for worker in self.worker_list:
            worker.stop_worker()
        sys.exit(0)


class ThreadWorker(threading.Thread):

    def __init__(self, id, scheduler):
        self.id = id
        self.scheduler = scheduler
        super().__init__()
        self.stop = False

    def do(self):
        if self.scheduler.queue.qsize() != 0:
            task_id, func, args, kwargs = self.scheduler.get_task()
            try:
                LOGGER.debug('Start task #{}'.format(task_id))
                result = func(*args, **kwargs)
                self.scheduler.add_result(task_id, self.id, result)
                LOGGER.debug('Task #{} done'.format(task_id))
            except Exception as ex:
                print(colored(ex, 'red'))
                LOGGER.error('Error during tasks #{} with worker #{}'.format(
                    task_id, self.id)
                )
                self.scheduler.add_result(task_id, self.id, ex)

    def run(self):
        while self.stop is False:
            try:
                self.do()
                time.sleep(1)
            except KeyboardInterrupt:
                LOGGER.error('KI')

    def stop_worker(self):
        self.stop = True
