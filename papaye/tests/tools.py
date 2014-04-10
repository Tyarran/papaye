import os

from pyramid import testing
from pyramid_beaker import set_cache_regions_from_settings


HERE = os.path.abspath(os.path.dirname(__name__))
TEST_RESOURCES = os.path.join('..', '..', HERE, 'test-resources')


class FakeGRequestResponse():
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


class FakeMatchedDict(object):

    def __init__(self, name):
        self.name = name


class TestRequest(testing.DummyRequest):

    def __init__(self, *args, **kwargs):
        super(TestRequest, self).__init__(*args, **kwargs)
        self.matched_route = FakeMatchedDict('')


class FakeRoute():

    def __init__(self, name):
        self.name = name


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
            'version': '1.0.0',
        }
    }
    for document in (package1, package2, release1):
        db.insert(document)


def create_test_app(config):
    """ This function returns a Pyramid WSGI application for functional tests.
    """
    config.include('pyramid_jinja2')
    set_cache_regions_from_settings(config.registry.settings)
    config.add_jinja2_search_path("papaye:templates")
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('simple', '/simple/*traverse', factory='papaye:root_factory')
    config.scan()
    return config.make_wsgi_app()
