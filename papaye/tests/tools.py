import os

from pyramid import testing


HERE = os.path.abspath(os.path.dirname(__name__))
TEST_RESOURCES = os.path.join('..', '..', HERE, 'test-resources')


class FakeMatchedDict(object):

    def __init__(self, name):
        self.name = name


class TestRequest(testing.DummyRequest):

    def __init__(self, *args, **kwargs):
        super(TestRequest, self).__init__(*args, **kwargs)
        self.matched_route = FakeMatchedDict('')


class FakeProducer(object):

    def __init__(self, *args, **kwargs):
        pass

    def send_pyobj(self, val):
        pass


def create_test_documents(db):
    package1 = {
        'type': 'package',
        'name': 'package1',
    }
    package2 = {
        'type': 'package',
        'name': 'package2',
    }
    release1 = {
        'type': 'release',
        'name': 'file-1.0.tar.gz',
        'package': 'package1',
    }
    for document in (package1, package2, release1):
        db.insert(document)


def create_db():
    from CodernityDB.database import Database
    db = Database('test_papaye')
    if not db.exists():
        db.create()
        from papaye.indexes import INDEXES
        for name, cls in INDEXES:
            index = cls(db.path, name)
            db.add_index(index)
        create_test_documents(db)
    else:
        db.open()
    return db
