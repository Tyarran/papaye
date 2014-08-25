import hashlib

from docutils.core import publish_parts
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from papaye.views.commons import BaseView
from papaye.models import Package, ReleaseFile


@view_config(route_name="browse", renderer='browse.jinja2')
class BrowseView(BaseView):

    def get_package(self, context):
        if not isinstance(context, Package):
            return self.get_package(context.__parent__)
        return context

    def get_release(self, context):
        if isinstance(context, Package):
            return context.get_last_release()
        elif isinstance(context, ReleaseFile):
            return context.__parent__
        else:
            return context

    def get_release_file(self, release):
        '''Return the .tar.gz first or other file'''
        tar_gz = [name for name in release.release_files.keys() if name.endswith('.tar.gz')]
        if tar_gz:
            return release[tar_gz[0]]
        return next((release_file for release_file in release.release_files.values()))

    def __call__(self):
        if not self.context:
            return HTTPNotFound()
        package = self.get_package(self.context)
        release = self.get_release(self.context)
        release_file = self.get_release_file(release)
        metadata = release.metadata
        maintainer_email = 'maintainer_email' in metadata and metadata['maintainer_email']
        maintainer_email = metadata['maintainer_email'] if maintainer_email else metadata['author_email']
        md5hash = hashlib.md5(maintainer_email.encode('latin-1')).hexdigest()
        description = publish_parts(metadata['description'], writer_name='html')
        return {
            'package': package,
            'release': release,
            'gravatar_hash': md5hash,
            'description': description,
            'release_file': release_file,
            'release_url': self.request.resource_url(
                release_file,
                route_name='simple',
            )
        }
