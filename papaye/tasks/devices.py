import multiprocessing
import pickle
import traceback
import zmq
import zmq.green

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pyramid.config import ConfigurationError
from pyramid.registry import global_registry
from zmq.devices import ProcessDevice

from papaye.tasks import TaskRegistry


def start_collector(settings):
    cache_manager = CacheManager(**parse_cache_config_options(settings))
    cache = cache_manager.get_cache_region('result_cache', 'result')
    global_registry.result_cache = cache

    def run():
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(settings.get('proxy.collector_socket'))

        while True:
            data = socket.recv()
            task_id, value = pickle.loads(data)
            cache.set_value(task_id, value)
    process = multiprocessing.Process(target=run)
    process.start()


def get_producer(settings):
    context = zmq.Context()
    socket = context.socket(zmq.XREQ)
    socket.connect(settings.get('proxy.broker'))
    return socket


def start_queue(settings):
    if 'proxy.broker' not in settings:
        raise ConfigurationError('"proxy.broker" missing in settings')
    if 'proxy.worker_socket' not in settings:
        raise ConfigurationError('"proxy.worker_socket" missing in settings')
    queuedevice = ProcessDevice(zmq.QUEUE, zmq.XREP, zmq.XREQ)
    queuedevice.bind_in(settings.get('proxy.broker'))
    queuedevice.bind_out(settings.get('proxy.worker_socket'))
    queuedevice.start()


def run_consumer(settings):
    context = zmq.green.Context()
    socket = context.socket(zmq.green.XREP)
    socket.connect(settings.get('proxy.worker_socket'))
    socket2 = context.socket(zmq.green.PUSH)
    socket2.connect(settings.get('proxy.collector_socket'))
    while True:
        data = socket.recv_multipart()[2]
        task_id, func_name, args, kwargs = pickle.loads(data)
        func = TaskRegistry()._tasks[func_name]
        func.task_id = task_id
        print 'Starting task id: {}'.format(func.task_id)
        try:
            result = func(*args, **kwargs)
            socket2.send_pyobj((task_id, result))
            print 'Task #{} finished'.format(func.task_id)
        except:
            traceback.print_exc()
            print 'Task #{} Error'.format(func.task_id)
