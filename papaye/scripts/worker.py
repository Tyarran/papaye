#import zmq
import gevent
import gevent.pool
import pickle
import sys
import traceback
import zmq.green as zmq

from papaye.scripts.common import get_settings
from papaye.tasks import TaskRegistry
from papaye.tasks.devices import run_consumer

__import__('papaye.tasks.download')


def main(*argv, **kwargs):
    group = gevent.pool.Group()
    settings = get_settings(sys.argv[1])
    for func in (run_consumer, ):
        device = gevent.spawn(func, settings)
        group.add(device)
    group.join()
