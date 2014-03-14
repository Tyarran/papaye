import os

from pyramid import testing
from pyramid.view import view_config
from pyramid_beaker import set_cache_regions_from_settings


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
        'info': {
            'md5_digest': 'Fake MD5',
        }
    }
    for document in (package1, package2, release1):
        db.insert(document)


def create_db(request=None, with_doc=True):
    from CodernityDB.database import Database
    db = Database('test_papaye')
    if not db.exists():
        db.create()
        from papaye.indexes import INDEXES
        for name, cls in INDEXES:
            index = cls(db.path, name)
            db.add_index(index)
        if with_doc:
            create_test_documents(db)
    else:
        db.open()
    return db


def create_test_app(config):
    """ This function returns a Pyramid WSGI application for functional tests.
    """
    config.include('pyramid_jinja2')
    set_cache_regions_from_settings(config.registry.settings)
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('repository', 'repository')
    config.add_route('simple', '/simple/')
    config.add_route('simple_release', '/simple/{package}/')
    config.add_route('download_release', '/simple/{package}/{release}')
    config.add_request_method(create_db, 'db', reify=True)
    config.scan()
    config.db = create_db()
    return config.make_wsgi_app()
