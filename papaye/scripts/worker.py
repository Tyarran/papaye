##import zmq
##import gevent
##import gevent.pool
#import multiprocessing
#import sys

#from papaye.scripts.common import get_settings
#from papaye.tasks.devices import run_consumer

#__import__('papaye.tasks.download')


#def main(*argv, **kwargs):
#    #group = multiprocess.pool.Group()
#    settings = get_settings(sys.argv[1])
#    #for func in (run_consumer, ):
#    process = multiprocessing.Process(func, settings)
#    process.start()
#        #group.add(device)
#    process.join()
