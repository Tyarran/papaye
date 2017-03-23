import contextlib
import os
import pytest
import shutil

from pyramid import testing


@pytest.fixture
def env():
    settings = {}
    request = testing.DummyRequest()
    config = testing.setUp(settings=settings, request=request)
    return {
        'request': request,
        'config': config,
        'settings': settings,
    }


@pytest.fixture
def packages_directory(env, tmpdir, request):
    settings = {
        'papaye.proxy': False,
        'papaye.packages_directory': tmpdir.strpath,
        'pyramid.incluces': 'pyramid_zodbconn',
    }
    env['settings'].update(settings)
    env['config'].include('pyramid_zodbconn')

    def clean_tmp_dir():
        if os.path.exists(tmpdir.strpath):
            shutil.rmtree(tmpdir.strpath)

    request.addfinalizer(clean_tmp_dir)
    return tmpdir.strpath


@pytest.fixture
def tmp_repo_dir(tmpdir):

    @contextlib.contextmanager
    def tmp_dir():
        yield tmpdir.strpath
        if os.path.exists(tmpdir.strpath):
            shutil.rmtree(tmpdir.strpath)

    return tmp_dir


@pytest.fixture
def routes(env, packages_directory):
    env['config'].add_route(
        'simple',
        '/simple/*traverse',
        factory='papaye.factories.root:repository_root_factory'
    )


@pytest.fixture
def request_factory(*args, **kwargs):
    def build_request(*args, **kwargs):
        request = testing.DummyRequest(*args, **kwargs)
        return request
    return build_request


@pytest.fixture
def config_factory(*args, **kwargs):
    def build_configurator(*args, **kwargs):
        return testing.setUp(*args, **kwargs)
    return build_configurator


@pytest.fixture
def repo_configuration(request, request_factory, tmpdir, config_factory):
    settings = {
        'papaye.proxy': False,
        'papaye.packages_directory': tmpdir.strpath,
        'pyramid.incluces': 'pyramid_zodbconn',
    }
    req = request_factory()
    config = config_factory(settings=settings, request=req)
    config.add_route(
        'simple',
        '/simple/*traverse',
        factory='papaye.factories.root:repository_root_factory'
    )

    def clean_tmp_dir():
        if os.path.exists(tmpdir.strpath):
            shutil.rmtree(tmpdir.strpath)

    request.addfinalizer(clean_tmp_dir)
