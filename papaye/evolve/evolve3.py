from papaye.schemas import Metadata, NullableMapping


def evolve(context):
    root = context['repository']
    schema = Metadata(typ=NullableMapping(), default=None)

    for package in root:
        print(package.name)
        for release in package:
            original_metadata = release.original_metadata
            serialized_metadata = schema.serialize(original_metadata)
            release.metadata = schema.deserialize(serialized_metadata)
    context.evolved = 3
