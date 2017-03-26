import os
import shutil
import tempfile
import uuid

from papaye.evolve.managers import load_model, context_from_root, APP_ROOT_NAME
from papaye.evolve.managers import EvolveError
from papaye.config.utils import SettingsReader

__doc__ = ''.join('Data migration. Migrate release files into a directory '
                  'instead of managed with ZODB blob storage')


def compute_release_file_directory(release_file):
    time_low = release_file.uuid.time_low
    path = list(map(lambda x: hex(int(x)), str(time_low)))
    return os.path.join(*path)


@load_model('papaye.evolve.models.snapshot2')
def evolve(root, config):
    from papaye.models import Root, Package, Release, ReleaseFile, User
    context =  context_from_root(root)
    repository = context['repository']
    for package in repository:
        package.root = package.__parent__
        delattr(package, '__parent__')
        for release in package:
            release.package = release.__parent__
            delattr(release, '__parent__')
            for release_file in release:
                release_file.release = release_file.__parent__
                delattr(release_file, '__parent__')
    context.evolved = 8
    return context
