from marshmallow import Serializer, fields


class PackageListSerializer(Serializer):
    name = fields.String()
    summary = fields.Method('get_summary')

    def get_summary(self, package):
        return package.metadata.get('summary')


class PackageSerializer(Serializer):
    name = fields.String()
    metadata = fields.Method('get_metadata')

    def get_metadata(self, package):
        return package.metadata


class ReleaseSerializer(Serializer):
    name = fields.Method('get_package_name')
    metadata = fields.Method('get_metadata')

    def get_package_name(self, release):
        return release.__parent__.name

    def get_metadata(self, release):
        return release.metadata
