import factory

from papaye import models


class RootFactory(factory.Factory):
    name = factory.Sequence(lambda n: 'Root{}'.format(n))

    class Meta:
        model = models.Root


class PackageFactory(factory.Factory):
    name = factory.Sequence(lambda n: 'Package{}'.format(n))
    __parent__ = factory.SubFactory(RootFactory)

    class Meta:
        model = models.Package


class ReleaseFactory(factory.Factory):
    version = factory.Sequence(lambda n: 'Release{}'.format(n))
    # version = '1.0'
    metadata = {}
    deserialize_metadata = True
    __parent__ = factory.SubFactory(PackageFactory)

    class Meta:
        model = models.Release


class ReleaseFileFactory(factory.Factory):
    filename = factory.Sequence(lambda n: 'ReleaseFile{}.tar.gz'.format(n))
    content = b'a content'
    status = models.STATUS.local
    __parent__ = factory.SubFactory(ReleaseFactory)

    class Meta:
        model = models.ReleaseFile
