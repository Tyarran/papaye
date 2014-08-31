from papaye.schemas import Metadata


def evolve(context):
    root = context['repository']
    schema = Metadata()

    for package_name in root:
        package = root[package_name]
        for release_name in package.releases:
            release = package[release_name]
            metadata = dict(((key, value) for key, value in release.metadata.items() if value is not None))
            release.original_metadata = dict(release.metadata)
            deserialized_metadata = schema.deserialize(metadata)
            release.metadata = deserialized_metadata
    context.evolved = 1
