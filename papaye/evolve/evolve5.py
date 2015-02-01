from papaye.models import STATUS


def evolve(context):
    root = context['repository']
    local_package = [release_file
                     for release in root
                     for release_file in release
                     if None in release_file.original_metadata]
    release_files = [release_file
                     for release in root
                     for release_file in release]

    for release_file in release_files:
        if release_file in local_package:
            release_file.status = STATUS.local
            print(release_file.__name__ + ' --> local')
        else:
            release_file.status = STATUS.cached
            print(release_file.__name__ + ' --> cached')
    context.evolved = 4
