# import multiprocessing
import itertools
import logging
import pickle
import queue
import threading
import time
import traceback
import zmq

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

# from beaker.cache import CacheManager
# from beaker.util import parse_cache_config_options
# from pyramid.registry import global_registry

from papaye.tasks import TaskRegistry


logger = logging.getLogger(__name__)


class Device(threading.Thread):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.settings = self.config.registry.settings
        self.go = True

    def get_socket(self):
        raise NotImplemented()

    def run(self):
        raise NotImplemented()


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

    def add_result(self, worker_id, result):
        raise NotImplemented()

    def status(self, task_id):
        raise NotImplemented()


class MultiThreadScheduler(IScheduler):

    def __init__(self, workers=1):
        self.workers = workers
        self.queue = queue.Queue()
        self.results = {}
        self.counter = itertools.count(1)

    def start(self):
        logging.info('Start {} scheduler'.format(self.__class__.__name__))
        for index in range(1, self.workers + 1):
            worker = ThreadWorker(index, self)
            worker.start()

    def add_task(self, *args):
        self.queue.put((self.task_id(args), args))

    def task_id(self, task_tuple):
        return next(self.counter)

    def get_task(self):
        if self.queue.qsize() == 0:
            return None
        return self.queue.get()

    def add_result(self, task_id, worker_id, result):
        self.results[task_id] = (worker_id, result)

    def status(self, task_id):
        return self.results[task_id]


class ThreadWorker(threading.Thread):

    def __init__(self, id, scheduler):
        self.id = id
        self.scheduler = scheduler
        super().__init__()

    def do(self):
        if self.scheduler.queue.qsize() != 0:
            task_id, item = self.scheduler.get_task()
            result = item[0](*item[1:])
            self.scheduler.add_result(task_id, self.id, result)

    def run(self):
        while True:
            logger.info('loop')
            self.do()
            time.sleep(1)


class Scheduler(object):

    def __init__(self, settings, config):
        self.config = config
        self.settings = settings
        self.concurrency = int(self.settings.get('papaye.worker.concurrency', 1))
        self.devices = []

    def run(self):
        self.devices.append(QueueDevice(self.config))
        # self.devices.append(CollectorDevice(self.config))
        for index in range(1, self.concurrency + 1):
            self.devices.append(ConsumerDevice(self.config, index, next(COLORS_GEN)))
        for device in self.devices:
            device.daemon = True
            device.start()


class Producer(object):

    def __init__(self, config):
        self.config = config
        self.settings = self.config.registry.settings
        self.socket = self.get_socket()

    def get_socket(self):
        context = zmq.Context()
        socket = context.socket(zmq.XREQ)
        socket.connect(self.settings.get('papaye.proxy.broker'))
        return socket


class ConsumerDevice(Device):

    def __init__(self, config, worker_number, color):
        super().__init__(config)
        self.worker_number = worker_number
        self.color = color
        # Load tasks
        __import__("papaye.tasks.download")

    def get_sockets(self):
        context = zmq.Context()
        socket = context.socket(zmq.XREP)
        socket.connect(self.settings.get('papaye.proxy.worker_socket'))
        socket2 = context.socket(zmq.PUSH)
        socket2.connect(self.settings.get('papaye.proxy.collector_socket'))
        return socket, socket2

    def run(self):
        logger.info(colored('Starting worker #{}'.format(self.worker_number), self.color))
        self.worker_socket, self.collector_socket = self.get_sockets()
        worker_number = self.worker_number
        while self.go:
            try:
                data = self.worker_socket.recv_multipart()[2]
                task_id, func_name, args, kwargs = pickle.loads(data)
                func = TaskRegistry()._tasks[func_name]
                func.task_id = task_id
                logger.info(colored('Worker {}: Starting task id: {}'.format(worker_number, func.task_id), self.color))
                try:
                    func(self.config, *args, **kwargs)
                    logger.info(colored('Worker {}: Task #{} finished'.format(
                        worker_number,
                        func.task_id
                    ), self.color))
                except Exception as exc:
                    formated_tb = traceback.format_tb(exc.__traceback__)
                    logger.error(colored('Worker {}: Task #{} Error\n{}'.format(
                        worker_number,
                        func.task_id,
                        formated_tb
                    ), self.color))
            except KeyboardInterrupt:
                self.go = False


class QueueDevice(Device):

    def __init__(self, config):
        super().__init__(config)
        # self.frontend, self.backend = self.get_sockets()

    def get_sockets(self):
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.XREP)
        frontend.bind(self.settings.get('papaye.proxy.broker'))
        # Socket facing services
        backend = context.socket(zmq.XREQ)
        backend.bind(self.settings.get('papaye.proxy.worker_socket'))
        return frontend, backend

    def run(self):
        logger.debug('Starting {} device'.format(self._name))
        try:
            self.frontend, self.backend = self.get_sockets()
            zmq.device(zmq.QUEUE, self.frontend, self.backend)
        except KeyboardInterrupt:
            pass


# class CollectorDevice(Device):

#     def __init__(self, config):
#         super().__init__(config)
#         cache_manager = CacheManager(**parse_cache_config_options(self.settings))
#         self.cache = cache_manager.get_cache_region('result_cache', 'result')
#         global_registry.result_cache = self.cache

#     def get_socket(self):
#         context = zmq.Context()
#         socket = context.socket(zmq.PULL)
#         socket.bind(self.settings.get('proxy.collector_socket'))
#         return socket

#     def run(self):
#         socket = self.get_socket()
#         while self.go:
#             try:
#                 data = socket.recv()
#                 task_id, value = pickle.loads(data)
#                 if value:
#                     self.cache.set_value(task_id, value)
#                 else:
#                     self.cache.set_value(task_id, 2)
#             except KeyboardInterrupt:
#                 self.go = False
