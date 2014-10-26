import colander

from docutils.core import publish_parts


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
    version = colander.SchemaNode(String(), missing=None)
    author = colander.SchemaNode(String(), missing=None)
    author_email = colander.SchemaNode(String(), missing=None)
    home_page = colander.SchemaNode(String(), missing=None)
    keywords = colander.SchemaNode(Tags(), default=[])
    license = colander.SchemaNode(String(), missing=None)
    summary = colander.SchemaNode(String(), missing=None)
    maintainer = colander.SchemaNode(String(), missing=None)
    maintainer_email = colander.SchemaNode(String(), missing=None)
    description = colander.SchemaNode(Description(), default=None)
    platform = colander.SchemaNode(String(), missing=None)
    classifiers = colander.SchemaNode(Classifiers(), default=[])
    name = colander.SchemaNode(String(), missing=None)


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
    platform = colander.SchemaNode(String(), missing=None)
    classifiers = colander.SchemaNode(Classifiers(), default=[])
    name = colander.SchemaNode(String(), missing=None)
