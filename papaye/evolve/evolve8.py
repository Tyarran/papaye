from papaye.evolve.managers import load_model, context_from_root

__doc__ = ''.join('Data migration. Get model \'__parent__\' '
                  'previous attributes and set the new  by model'
                  ' specific attribute')


@load_model('papaye.evolve.models.snapshot2')
def evolve(root, config):
    context = context_from_root(root)
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
