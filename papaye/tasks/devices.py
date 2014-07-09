import logging
import multiprocessing
import pickle
import signal
import traceback
import zmq

# from beaker.cache import CacheManager
# from beaker.util import parse_cache_config_options
# from pyramid.registry import global_registry

from papaye.tasks import TaskRegistry


logger = logging.getLogger(__name__)


class Device(multiprocessing.Process):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.settings = self.config.registry.settings
        self.go = True

    def get_socket(self):
        raise NotImplemented()

    def run(self):
        raise NotImplemented()


class Scheduler(object):

    def __init__(self, settings, config):
        self.config = config
        self.settings = settings
        self.concurency = int(self.settings.get('papaye.worker.concurency', 1))
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        self.devices = []

    def sigterm_handler(self, _signo, _stack_frame):
        for device in self.devices:
            if device._popen:
                device.terminate()

    def run(self):
        self.devices.append(QueueDevice(self.config))
        # self.devices.append(CollectorDevice(self.config))
        for index in range(1, self.concurency + 1):
            self.devices.append(ConsumerDevice(self.config, index))
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

    def __init__(self, config, worker_number):
        super().__init__(config)
        self.worker_number = worker_number
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
        logger.info('Starting worker {}'.format(self._name))
        self.worker_socket, self.collector_socket = self.get_sockets()
        worker_number = self.worker_number
        while self.go:
            try:
                data = self.worker_socket.recv_multipart()[2]
                task_id, func_name, args, kwargs = pickle.loads(data)
                func = TaskRegistry()._tasks[func_name]
                func.task_id = task_id
                logger.info('Worker {}: Starting task id: {}'.format(worker_number, func.task_id))
                try:
                    # result = func(self.settings, *args, **kwargs)
                    # result = func(self.config, *args, **kwargs)
                    func(self.config, *args, **kwargs)
                    # self.collector_socket.send(pickle.dumps((task_id, result)))
                    logger.info('Worker {}: Task #{} finished'.format(worker_number, func.task_id))
                except Exception as exc:
                    formated_tb = traceback.format_tb(exc.__traceback__)
                    logger.error('Worker {}: Task #{} Error\n{}'.format(worker_number, func.task_id, formated_tb))
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
