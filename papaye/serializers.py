import colander
import hashlib


from papaye.schemas import APIMetadata, String


class Serializer(object):
    fields = None
    _schema = None

    def __new__(cls, *args, **kwargs):
        attributes = {attribute_name: getattr(cls, attribute_name) for attribute_name in dir(cls)}
        cls.fields = {attribute_name: attribute for attribute_name, attribute in attributes.items()
                      if isinstance(attribute, colander.SchemaNode)}
        return super(Serializer, cls).__new__(cls)

    @property
    def schema(self):
        if self._schema is None:
            schema = colander.SchemaNode(colander.Mapping())
            nodes = {name: node for name, node in self.fields.items() if isinstance(node, colander.SchemaNode)}
            if nodes:
                for name, node in nodes.items():
                    node.name = name
                    schema.add(node)
                self._schema = schema
        return self._schema

    def serialize(self, obj):
        data = self.get_data(obj)
        cstruct = self.schema.serialize(data)
        return self.schema.deserialize(cstruct)

    def get_data(self, obj):
        return {key: getattr(obj, key) for key in self.fields.keys() if getattr(obj, key, None) is not None}


class PackageListSerializer(Serializer):
    name = colander.SchemaNode(colander.String())
    summary = colander.SchemaNode(colander.String())

    def get_data(self, package):
        data = super().get_data(package)
        data['summary'] = package.metadata.get('summary')
        return data


class PackageAPISerializer(Serializer):
    name = colander.SchemaNode(String())
    version = colander.SchemaNode(String())
    gravatar_hash = colander.SchemaNode(String(), missing=None)
    metadata = APIMetadata()
    download_url = colander.SchemaNode(String())

    def __init__(self, request):
        self.request = request

    def hash(self, email):
        return hashlib.md5(email).hexdigest()

    def get_release_file(self, release):
        '''Return the .tar.gz first or other file'''
        tar_gz = [name for name in release.release_files.keys() if name.endswith('.tar.gz')]
        if tar_gz:
            return release[tar_gz[0]]
        elif len(list(release.release_files.values())):
            return next((release_file for release_file in release.release_files.values()))
        else:
            return None

    def get_data(self, package):
        data = super().get_data(package)
        data['metadata'] = package.metadata
        release = package.get_last_release()
        data['version'] = release.version
        if package.metadata['maintainer_email']:
            data['gravatar_hash'] = self.hash(package.metadata['maintainer_email'].encode('latin-1'))
        elif package.metadata['author_email']:
            data['gravatar_hash'] = self.hash(package.metadata['author_email'].encode('latin-1'))
        else:
            data['gravatar_hash'] = None
        release_file = self.get_release_file(release)
        data['download_url'] = self.request.resource_url(
            release_file,
            route_name='simple',
        )
        return data


class ReleaseSerializer(Serializer):
    name = colander.SchemaNode(colander.String())
    version = colander.SchemaNode(colander.String())
    metadata = APIMetadata()

    def get_data(self, release):
        return {
            'name': release.__parent__.name,
            'version': release.version,
            'metadata': release.metadata,
        }
