import mock
import pytest
import queue
import time


# def test_scheduler_instanciate():
#     from papaye.tasks.devices import Scheduler
#     result = Scheduler() #     assert result.concurency == 1
#     assert result.combined
#     assert hasattr(result, 'queue')
#     assert isinstance(result.queue, queue.Queue)


# def test_scheduler_instanciate_with_parameter():
#     from papaye.tasks.devices import Scheduler

#     result = Scheduler(concurency=2, combined=False)

#     assert result.concurency == 2
#     assert result.combined is False
#     assert hasattr(result, 'queue')
#     assert isinstance(result.queue, queue.Queue)


# def test_scheduler_add_async_task():
#     from papaye.tasks.devices import Scheduler
#     scheduler = Scheduler()
#     assert scheduler.queue.qsize() == 0

#     scheduler.add_async_task(time.sleep, 0.1)

#     assert scheduler.queue.qsize() == 1
#     assert scheduler.queue.get() == (time.sleep, 0.1)


# def test_scheduler_get_task():
#     from papaye.tasks.devices import Scheduler
#     scheduler = Scheduler()
#     scheduler.add_async_task(time.sleep, 0.1)
#     assert scheduler.queue.qsize() == 1

#     result = scheduler.get_task()

#     assert result == (time.sleep, 0.1)
#     assert scheduler.queue.qsize() == 0


# def test_scheduler_get_task_without_task_in_queue():
#     from papaye.tasks.devices import Scheduler
#     scheduler = Scheduler()
#     assert scheduler.queue.qsize() == 0

#     result = scheduler.get_task()

#     assert result is None
#     assert scheduler.queue.qsize() == 0

# def test_scheduler_start_worker():
#     from papaye.tasks.devices import Scheduler
#     scheduler = Scheduler()
#     scheduler.add_async_task(time.sleep, 0.1)


def test_scheduler_instanciate():
    from papaye.tasks.devices import MultiThreadScheduler

    result = MultiThreadScheduler(workers=2)

    assert hasattr(result, 'workers')
    assert result.workers == 2
    assert hasattr(result, 'queue')
    assert isinstance(result.queue, queue.Queue)
    assert result.queue.qsize() == 0
    assert result.results == {}


def test_scheduler_instanciate_without_workers_parameter():
    from papaye.tasks.devices import MultiThreadScheduler

    result = MultiThreadScheduler()

    assert hasattr(result, 'workers')
    assert result.workers == 1
    assert hasattr(result, 'queue')
    assert isinstance(result.queue, queue.Queue)
    assert result.queue.qsize() == 0
    assert result.results == {}


def test_scheduler_add_task():
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    assert scheduler.queue.qsize() == 0

    scheduler.add_task(time.sleep, 1)
    assert scheduler.queue.qsize() == 1


def test_scheduler_add_result():
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler()

    scheduler.add_result(1, 1, 'A result')

    assert scheduler.results == {1: (1, 'A result')}


@mock.patch('threading.Thread.start')
def test_scheduler_start(mock):
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler(workers=2)

    scheduler.start()

    assert mock.call_count == 2


def test_scheduler_status():
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    scheduler.results = {1: (1, None)}

    result = scheduler.status(1)

    assert result == (1, None)


def test_scheduler_status_task_id_not_exists():
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler()

    with pytest.raises(KeyError):
        scheduler.status(1)


def test_threadworker_instanciate():
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler
    scheduler = MultiThreadScheduler()

    result = ThreadWorker(id=1, scheduler=scheduler)

    assert result.id == 1
    assert result.scheduler == scheduler


@mock.patch('time.sleep')
def test_threadworker_do(mock):
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    scheduler.add_task(time.sleep, 1)
    worker = ThreadWorker(id=1, scheduler=scheduler)
    assert scheduler.queue.qsize() == 1

    worker.do()

    assert scheduler.queue.qsize() == 0
    assert mock.call_count == 1


def test_threadworker_do_with_own_function():
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler

    def test_func():
        pass

    scheduler = MultiThreadScheduler()
    scheduler.add_task(test_func)
    worker = ThreadWorker(id=1, scheduler=scheduler)
    assert scheduler.queue.qsize() == 1

    worker.do()

    assert scheduler.queue.qsize() == 0


def test_threadworker_do_with_result():
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler

    def test_func(value):
        return value

    scheduler = MultiThreadScheduler()
    scheduler.add_task(test_func, 42)
    worker = ThreadWorker(id=1, scheduler=scheduler)
    assert scheduler.queue.qsize() == 1

    worker.do()

    assert scheduler.queue.qsize() == 0
    assert scheduler.results == {1: (1, 42)}
