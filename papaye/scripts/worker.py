#import zmq
import gevent
import gevent.pool
import pickle
import sys
import traceback
import zmq.green as zmq

from papaye.scripts.common import get_settings


def run_consumer(settings):
    context = zmq.Context()
    socket = context.socket(zmq.XREP)
    socket.connect(settings.get('proxy.worker_socket'))
    socket2 = context.socket(zmq.PAIR)
    socket2.connect(settings.get('proxy.collector_socket'))
    while True:
        data = socket.recv_multipart()[2]
        task_id, func, args, kwargs = pickle.loads(data)
        func.task_id = task_id
        print 'Starting task id: {}'.format(func.task_id)
        try:
            result = func(*args, **kwargs)
            socket2.send_pyobj(result)
            print 'Task #{} finished'.format(func.task_id)
        except:
            traceback.print_exc()
            print 'Task #{} Error'.format(func.task_id)


def run_collector(settings):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(settings.get('proxy.collector_socket'))
    while True:
        print pickle.loads(socket.recv())


def main(*argv, **kwargs):
    group = gevent.pool.Group()
    settings = get_settings(sys.argv[1])
    for func in (run_consumer, run_collector):
        device = gevent.spawn(func, settings)
        group.add(device)
    group.join()
