import colander


class Tags(object):

    def serialize(self, node, appstruct):
        if not isinstance(appstruct, list):
            raise colander.Invalid(node, '%r is not a list' % appstruct)
        else:
            return ' '.join(appstruct)

    def deserialize(self, node, cstruct):
        if cstruct == colander.null:
            return None
        elif isinstance(cstruct, (tuple, list)):
            return cstruct
        elif not isinstance(cstruct, (str, bytes)):
            raise colander.Invalid(node, '%r is not a string' % cstruct)
        else:
            return cstruct.split(' ')


class Classifiers(object):

    def serialize(self, node, appstruct):
        if not isinstance(appstruct, list):
            raise colander.Invalid(node, '%r is not a list' % appstruct)
        else:
            return '\n'.join(appstruct)

    def deserialize(self, node, cstruct):
        if cstruct == colander.null:
            return None
        elif isinstance(cstruct, (str, bytes)):
            return [value for value in (value.strip() for value in cstruct.split('\n')) if value != '']
        elif isinstance(cstruct, list):
            return cstruct
        else:
            raise colander.Invalid(node, '%r is not a string or list' % cstruct)


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
