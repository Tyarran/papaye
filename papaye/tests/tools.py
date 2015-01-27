import colander
import os
import shutil
import tempfile

from pyramid import testing
from pyramid_beaker import set_cache_regions_from_settings
from ZODB.blob import BlobStorage
from ZODB.DB import DB
from ZODB.MappingStorage import MappingStorage

from papaye.models import BaseModel
from papaye.scripts.initialize import create_app_root
from papaye.serializers import Serializer


HERE = os.path.abspath(os.path.dirname(__name__))
TEST_RESOURCES = os.path.join('..', '..', HERE, 'test-resources')


def get_resource(*args):
    return os.path.join(TEST_RESOURCES, *args)


class FakeGRequestResponse():

    def __init__(self, status_code, content, url="https://fake/url/"):
        self.status_code = status_code
        self.content = content
        self.url = url


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


def get_db_connection(blob_dir):
    storage = MappingStorage('test')
    blob_storage = BlobStorage(blob_dir, storage)
    db = DB(blob_storage)
    conn = db.open()
    create_app_root(conn)
    return conn


def set_database_connection(request, blob_dir=None, config=None):
    if not blob_dir:
        blob_dir = tempfile.mkdtemp('blobs')
    conn = get_db_connection(blob_dir)
    request._primary_zodb_conn = conn
    if config:
        import transaction
        conn.root()['repository'] = {}
        conn.root()['user'] = {}
        transaction.commit()
        config.registry._zodb_databases = {'': conn._db}
    return blob_dir


def remove_blob_dir(blob_dir):
    shutil.rmtree(blob_dir)


def disable_cache(settings=None):
    cache_settings = {
        'cache.regions': 'pypi',
        'cache.enabled': 'false',
    }
    if settings:
        settings.update(cache_settings)
    else:
        settings = cache_settings
    set_cache_regions_from_settings(settings)
    return settings


def mock_proxy_response(mock):
    with open(get_resource('pyramid.json'), 'rb') as pyramid_json:
        pypi_response = FakeGRequestResponse(200, pyramid_json.read())
    mock.return_value = pypi_response


class TestModel(BaseModel):

    def __init__(self, value):
        self.value = value


class TestSerializer(Serializer):
    model = TestModel
    value = colander.SchemaNode(colander.String())
