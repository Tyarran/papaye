import os

import colander

from docutils.core import publish_parts

from papaye.evolve.managers import load_model, context_from_root


class String(colander.String):

    def serialize(self, node, appstruct):
        if appstruct is None:
            appstruct = colander.null
        return super().serialize(node, appstruct)


class Tags(object):

    def serialize(self, node, appstruct):
        if appstruct is None:
            return colander.null
        elif isinstance(appstruct, (str, bytes)):
            return [str(elem) for elem in appstruct.split(' ')]
        elif isinstance(appstruct, list):
            return [str(elem) for elem in appstruct]
        else:
            raise colander.Invalid(node, '%r is not a list or string')

    def deserialize(self, node, cstruct):
        if cstruct == colander.null:
            return None
        elif isinstance(cstruct, (tuple, list)):
            return cstruct
        elif not isinstance(cstruct, (str, bytes)):
            raise colander.Invalid(node, '%r is not a string' % cstruct)
        else:
            return cstruct.split(' ')


class Classifiers(colander.List):

    def deserialize(self, node, cstruct):
        if cstruct == colander.null:
            return None
        elif isinstance(cstruct, (str, bytes)):
            return [value for value in (value.strip() for value in cstruct.split('\n')) if value != '']
        elif isinstance(cstruct, list):
            return cstruct
        else:
            raise colander.Invalid(node, '%r is not a string or list' % cstruct)


class Description(object):

    def serialize(self, node, appstruct):
        if appstruct is None:
            return colander.null
        if not isinstance(appstruct, (str, bytes)):
            raise colander.Invalid(node, '%r is not a string' % appstruct)
        return appstruct

    def deserialize(self, node, cstruct):
        if cstruct == colander.null:
            return None
        if not isinstance(cstruct, (str, bytes)):
            raise colander.Invalid(node, '%r is not a string' % cstruct)
        else:
            try:
                return {'content': publish_parts(cstruct, writer_name='html')['fragment'], 'html': True}
            except:
                return {'content': cstruct, 'html': False}


class APIDescription(colander.MappingSchema):
    content = colander.SchemaNode(colander.String())
    html = colander.SchemaNode(colander.Boolean())


class Metadata(colander.MappingSchema):
    version = colander.SchemaNode(colander.String(), missing=None)
    author = colander.SchemaNode(colander.String(), missing=None)
    author_email = colander.SchemaNode(colander.String(), missing=None)
    home_page = colander.SchemaNode(colander.String(), missing=None)
    keywords = colander.SchemaNode(Tags(), missing=None)
    license = colander.SchemaNode(colander.String(), missing=None)
    summary = colander.SchemaNode(colander.String(), missing=None)
    maintainer = colander.SchemaNode(colander.String(), missing=None)
    maintainer_email = colander.SchemaNode(colander.String(), missing=None)
    description = colander.SchemaNode(colander.String(), missing=None)
    platform = colander.SchemaNode(colander.String(), missing=None)
    classifiers = colander.SchemaNode(Classifiers(), missing=None)
    name = colander.SchemaNode(colander.String(), missing=None)


class APIMetadata(colander.MappingSchema):
    version = colander.SchemaNode(String(), missing=None)
    author = colander.SchemaNode(String(), missing=None)
    author_email = colander.SchemaNode(String(), missing=None)
    home_page = colander.SchemaNode(String(), missing=None)
    keywords = colander.SchemaNode(Tags(), default=[])
    license = colander.SchemaNode(String(), missing=None)
    summary = colander.SchemaNode(String(), missing=None)
    maintainer = colander.SchemaNode(String(), missing=None)
    maintainer_email = colander.SchemaNode(String(), missing=None)
    description = APIDescription()
    platform = colander.SchemaNode(colander.String(), missing=None)
    classifiers = colander.SchemaNode(Classifiers(), default=[])
    name = colander.SchemaNode(colander.String(), missing=None)


@load_model('papaye.evolve.models.snapshot1')
def evolve(root):
    context = context_from_root(root)
    repository = context['repository']
    schema = Metadata()

    for package_name in repository:
        package = repository[package_name]
        for release_name in package.releases:
            release = package[release_name]
            metadata = dict(((key, value) for key, value in release.metadata.items() if value is not None))
            release.original_metadata = dict(release.metadata)
            deserialized_metadata = schema.deserialize(metadata)
            release.metadata = deserialized_metadata

            for release_filename in release.release_files:
                release_file = release[release_filename]
                release_file.size = os.path.getsize(release_file.content.open().name)
    context.evolved = 1
