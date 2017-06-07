import colander


class Path(colander.MappingSchema):
    package_name = colander.SchemaNode(colander.String())
    version = colander.SchemaNode(colander.String(), missing=None)
    filename = colander.SchemaNode(colander.String(), missing=None)


class GetPackageSchema(colander.MappingSchema):
    path = Path()
