import pickle
import sys
import zmq
import traceback

from papaye.scripts.common import get_settings


def run_consumer(settings):
    context = zmq.Context()
    socket = context.socket(zmq.XREP)
    socket.connect(settings.get('proxy.worker_socket'))
    while True:
        data = socket.recv_multipart()[2]
        task_id, func, args, kwargs = pickle.loads(data)
        func.task_id = task_id
        print 'Starting task id: {}'.format(func.task_id)
        try:
            func(*args, **kwargs)
            print 'Task #{} finished'.format(func.task_id)
        except:
            traceback.print_exc()
            print 'Task #{} Error'.format(func.task_id)


def main(*argv, **kwargs):
    settings = get_settings(sys.argv[1])
    run_consumer(settings)
