from papaye.evolve.managers import load_model, context_from_root, APP_ROOT_NAME


__doc__ = 'blablabla blablabla'


@load_model('papaye.evolve.models.snapshot2')
def evolve(root, config=None):
    from papaye.models import Root, Package, Release, ReleaseFile, User
    new_root = Root()
    new_root['repository'] = Root()
    context = context_from_root(root)
    for package_name in context.get('repository', tuple()):
        package = context['repository'][package_name]
        new_root['repository'][package_name] = Package(package.name)

        for release_name in package.releases:
            release = package[release_name]
            try:
                new_root['repository'][package_name][release_name] = Release(
                    release.__name__, release.__name__, release.original_metadata
                )
                for release_filename in release.release_files:
                    release_file = release[release_filename]
                    new_root['repository'][package_name][release_name][release_filename] = ReleaseFile(
                        release_file.filename, release_file.content.open().read(), release_file.md5_digest,
                        release_file.status,
                    )
            except:
                print('{} v{} is corrupt! He won\'t be imported'.format(package.__name__, release.__name__))
    new_root['user'] = Root()
    for username in context.get('user', tuple()):
        user = context['user'][username]
        new_user = User('', '')
        new_user.username = user.username
        new_user.password = user.password
        new_user.groups = user.groups
        new_root['user'][username] = new_user
    root[APP_ROOT_NAME] = new_root
    context.evolved = 6
    return context
