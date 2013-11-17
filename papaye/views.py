from os import listdir
from os.path import isdir, join
from pyramid.response import Response, FileResponse
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
)


SUPPORTED_PACKAGE_FORMAT = (
    '.egg',
    '.tar.gz',
    '.whl',
    '.zip',
)


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'papaye'}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_papaye_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


@view_config(route_name="simple", renderer="simple.jinja2")
@view_config(route_name="simple_release", renderer="simple.jinja2")
@view_config(route_name="download_release")
class SimpleView(object):

    def __init__(self, request):
        self.request = request
        self.settings = request.registry.settings
        self.repository = self.settings.get('papaye.repository')

    def list_packages(self):
        return ((e, self.request.route_path('simple', e))
                for e in sorted(listdir(self.repository))
                if isdir(join(self.repository, e)))

    def list_releases(self):
        package = self.request.matchdict['package']
        releases_gen = ((e, self.request.route_path('simple', package, e))
                        for e in sorted(listdir(join(self.repository, package)))
                        if not isdir(join(self.repository, package, e))
                        and e[-3:] in SUPPORTED_PACKAGE_FORMAT
                        or e[-7:] in SUPPORTED_PACKAGE_FORMAT)
        return releases_gen, package

    def download_release(self):
        package = self.request.matchdict['package']
        release = self.request.matchdict['release']
        file_path = join(self.repository, package, release)
        return FileResponse(file_path)

    def __call__(self):
        if self.request.matched_route.name == 'simple':
            return {'objects': self.list_packages()}
        elif self.request.matched_route.name == 'simple_release':
            objs, package = self.list_releases()
            return {'objects': objs, 'package': package}
        else:
            return self.download_release()
