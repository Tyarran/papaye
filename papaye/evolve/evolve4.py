def evolve(context):
    root = context['repository']

    for package in root:
        package.__parent__ = root

        print('Upgrade {} package'.format(package.__name__))

        for release in package:
            release.__parent__ = package
            print('\tUpgrade {} release'.format(release.__name__))

            for release_file in release:
                release_file.__parent__ = release
                print('\t\tUpgrade {} file'.format(release_file.__name__))
    context.evolved = 4
