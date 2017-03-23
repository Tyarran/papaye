from papaye.evolve.managers import load_model, context_from_root


@load_model('papaye.evolve.models.snapshot1')
def evolve(root):
    context = context_from_root(root)
    repository = context['repository']

    for package_name in repository:
        package = repository[package_name]

        package.__parent__ = repository

        print('Upgrade {} package'.format(package.__name__))

        for release_name in package.releases:
            release = package[release_name]

            release.__parent__ = package
            print('\tUpgrade {} release'.format(release.__name__))

            for release_filename in release.release_files:
                release_file = release[release_filename]
                release_file.__parent__ = release
                print('\t\tUpgrade {} file'.format(release_file.__name__))
    context.evolved = 4
