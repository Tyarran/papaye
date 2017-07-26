import colander

from colander import MappingSchema, SchemaNode, SchemaType, Invalid
from pyramid.path import DottedNameResolver


class Class(SchemaType):

    def serialize(self, node, appstruct):
        pass

    def deserialize(self, node, cstruct):
        if callable(cstruct):
            return cstruct
        elif isinstance(cstruct, str):
            resolver = DottedNameResolver()
            scheduler = resolver.maybe_resolve(cstruct)
            return scheduler
        raise Invalid(node, '{} is not a valid Python dotted name'.format(
            cstruct
        ))


class Papaye(MappingSchema):
    debug = SchemaNode(colander.Boolean())
    proxy = SchemaNode(colander.Boolean())
    anonymous_install = SchemaNode(colander.Boolean())
    anonymous_browse = SchemaNode(colander.Boolean())
    packages_directory = SchemaNode(colander.String())
    cache = SchemaNode(colander.Boolean())
    scheduler = SchemaNode(Class())
    workers = SchemaNode(colander.Integer())
    open_repository = SchemaNode(colander.Boolean())


class Settings(colander.MappingSchema):
    papaye = Papaye()
