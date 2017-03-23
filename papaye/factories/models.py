import factory

from papaye import models


# class ParentAliasMixin(object):
#     parent_alias = 'attribute name'

#     # def _build(cls, *args, **kwargs):
#     #     import pdb; pdb.set_trace()

#     @classmethod
#     def create(cls, *args, **kwargs):
#         children_attr = [
#             key for key, _ in kwargs.items()
#             if '__' in key
#         ]

#         import pdb; pdb.set_trace()
#         for attr in children_attr:
#             attr_not_to_change = attr.split('__')[-1]
#             if attr.split('__')[-2] == cls._meta.model.parent_attr_name:
#             # if attr.split('__')[-2] == cls.parent_alias:
#                 value = kwargs.pop(attr)
#                 kwargs['__parent____' + attr_not_to_change] = value
#         print(kwargs)
#         return super().create(*args, **kwargs)


#     @classmethod
#     def _adjust_kwargs(cls, **kwargs):
#         kwargs = super()._adjust_kwargs(**kwargs)
#         if cls.parent_alias in kwargs:
#             parent = kwargs.pop(cls.parent_alias)
#             kwargs['__parent__'] = parent
#         return kwargs


class RootFactory(factory.Factory):
    name = factory.Sequence(lambda n: 'Root{}'.format(n))

    class Meta:
        model = models.Root


class PackageFactory(factory.Factory):
    name = factory.Sequence(lambda n: 'Package{}'.format(n))
    root = factory.SubFactory(RootFactory)

    class Meta:
        model = models.Package


class ReleaseFactory(factory.Factory):
    version = factory.Sequence(lambda n: 'Release{}'.format(n))
    metadata = {}
    deserialize_metadata = True
    package = factory.SubFactory(PackageFactory)

    class Meta:
        model = models.Release


class ReleaseFileFactory(factory.Factory):
    filename = factory.Sequence(lambda n: 'ReleaseFile{}.tar.gz'.format(n))
    content = b'a content'
    status = models.STATUS.local
    release = factory.SubFactory(ReleaseFactory)

    class Meta:
        model = models.ReleaseFile
