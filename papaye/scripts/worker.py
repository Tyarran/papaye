#import zmq
import gevent
import gevent.pool
import sys

from papaye.scripts.common import get_settings
from papaye.tasks.devices import run_consumer

__import__('papaye.tasks.download')


def main(*argv, **kwargs):
    group = gevent.pool.Group()
    settings = get_settings(sys.argv[1])
    for func in (run_consumer, ):
        device = gevent.spawn(func, settings)
        group.add(device)
    group.join()
