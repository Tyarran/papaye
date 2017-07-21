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
    context = context_from_root(root)
    settings = SettingsReader(config)
    packages_dir = settings.read_str('papaye.packages_directory')
    if os.path.exists(packages_dir):
        raise EvolveError('The repository directory is already exists. '
                          'Please remove them or choose another directory '
                          'in your settings file ({})'.format(
                              config.registry._settings.get('__file__', None)
                          ))
    tmpdir = tempfile.mkdtemp('packages_directory')
    for package in context['repository']:
        for release in package:
            for release_file in release:
                release_file.uuid = uuid.uuid4()
                pkg_dir_relative_path = compute_release_file_directory(
                    release_file
                )
                dir = os.path.join(tmpdir, pkg_dir_relative_path)
                os.makedirs(dir, exist_ok=True)
                path = os.path.join(dir, release_file.filename)
                with open(path, 'wb') as archive:
                    archive.write(release_file.content.open().read())
                release_file._path = pkg_dir_relative_path
                delattr(release_file, 'content')
    shutil.copytree(tmpdir, packages_dir)
    context.evolved = 7
    return context
