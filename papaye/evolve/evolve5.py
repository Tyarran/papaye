from papaye.models import STATUS
from papaye.evolve.managers import load_model, context_from_root


@load_model('papaye.evolve.models.snapshot1')
def evolve(root):
    context = context_from_root(root)
    repository = context['repository']

    for package_name in repository:
        package = repository[package_name]
        for release_name in package.releases:
            release = package[release_name]
            for release_filename in release.release_files:
                release_file = release[release_filename]
                if None in release.original_metadata:
                    release_file.status = STATUS.local
                    print(release_file.__name__ + ' --> local')
                else:
                    release_file.status = STATUS.cached
                    print(release_file.__name__ + ' --> cached')

    context.evolved = 4
