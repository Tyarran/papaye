import datetime
import mock
import pytest
import queue
import time


def test_scheduler_instanciate():
    from papaye.tasks.devices import MultiThreadScheduler

    result = MultiThreadScheduler(workers=2)

    assert hasattr(result, 'workers')
    assert result.workers == 2
    assert hasattr(result, 'queue')
    assert isinstance(result.queue, queue.Queue)
    assert result.queue.qsize() == 0
    assert result.results == {}
    assert result.status_history == {}
    assert result.worker_list == []


def test_scheduler_instanciate_without_workers_parameter():
    from papaye.tasks.devices import MultiThreadScheduler

    result = MultiThreadScheduler()

    assert hasattr(result, 'workers')
    assert result.workers == 1
    assert hasattr(result, 'queue')
    assert isinstance(result.queue, queue.Queue)
    assert result.queue.qsize() == 0
    assert result.results == {}
    assert result.status_history == {}
    assert result.worker_list == []


def test_scheduler_add_task():
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    assert scheduler.queue.qsize() == 0
    assert scheduler.status_history == {}

    scheduler.add_task(time.sleep, 1)

    assert scheduler.queue.qsize() == 1
    assert len(scheduler.results) == 1
    assert isinstance(scheduler.results, dict)
    assert scheduler.results[1] == {"status": 0, "result": None}
    assert len(scheduler.status_history) == 1
    assert list(scheduler.status_history.keys()) == [1, ]
    assert isinstance(scheduler.status_history[1], list)
    assert isinstance(scheduler.status_history[1][0], tuple)
    assert len(scheduler.status_history[1][0]) == 2
    assert scheduler.status_history[1][0][0] == 0
    assert isinstance(scheduler.status_history[1][0][1], datetime.datetime)


def test_scheduler_add_result():
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    now = datetime.datetime.now()
    scheduler.status_history = {1: [(0, now)]}

    scheduler.add_result(1, 1, 'A result')

    assert scheduler.results == {1: (1, 'A result')}
    assert isinstance(scheduler.status_history[1], list)
    assert isinstance(scheduler.status_history[1][0], tuple)
    assert scheduler.status_history[1][0][0] == 0
    assert scheduler.status_history[1][0][1] == now
    assert isinstance(scheduler.status_history[1][1], tuple)
    assert scheduler.status_history[1][1][0] == 2
    assert isinstance(scheduler.status_history[1][1][1], datetime.datetime)


@mock.patch('threading.Thread.start')
def test_scheduler_start(mock):
    from papaye.tasks.devices import MultiThreadScheduler
    scheduler = MultiThreadScheduler(workers=2)

    scheduler.start()

    assert mock.call_count == 2
    assert len(scheduler.worker_list) == 2


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
    mock.return_value = None
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


def test_threadworker_do_with_args_and_kwargs():
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler

    def test_func(*args, **kwargs):
        return args, kwargs

    scheduler = MultiThreadScheduler()
    scheduler.add_task(test_func, 'one', two='two')
    worker = ThreadWorker(id=1, scheduler=scheduler)
    assert scheduler.queue.qsize() == 1

    worker.do()

    assert scheduler.queue.qsize() == 0
    assert scheduler.results[1] == (1, (('one', ), {'two': 'two'}))


def test_threadworker_do_with_result():
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    worker = ThreadWorker(id=1, scheduler=scheduler)

    def test_func(value):
        return value

    scheduler.add_task(test_func, 42)
    assert scheduler.queue.qsize() == 1

    worker.do()

    assert scheduler.queue.qsize() == 0
    assert scheduler.results == {1: (1, 42)}


def test_threadworker_do_with_exception():
    from papaye.tasks.devices import ThreadWorker, MultiThreadScheduler
    scheduler = MultiThreadScheduler()
    worker = ThreadWorker(id=1, scheduler=scheduler)

    def test_func(value):
        raise Exception()

    scheduler.add_task(test_func, 42)
    assert scheduler.queue.qsize() == 1

    worker.do()

    assert scheduler.queue.qsize() == 0
    assert 1 in scheduler.results
    assert isinstance(scheduler.results[1], tuple)
    assert scheduler.results[1][0] == 1
    assert isinstance(scheduler.results[1][1], Exception)
