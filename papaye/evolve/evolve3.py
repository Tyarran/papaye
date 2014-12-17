from papaye.schemas import Metadata, NullableMapping


def evolve(context):
    root = context['repository']
    schema = Metadata(typ=NullableMapping(), default=None)

    for package_name in root:
        package = root[package_name]
        print(package_name)
        for release_name in package.releases:
            release = package[release_name]
            original_metadata = release.original_metadata
            serialized_metadata = schema.serialize(original_metadata)
            release.metadata = schema.deserialize(serialized_metadata)
    context.evolved = 3
