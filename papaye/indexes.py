from CodernityDB.hash_index import HashIndex
from hashlib import md5


class PackageIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '16s'
        super(PackageIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        name = data.get('name')
        datatype = data.get('type')
        if name is not None and datatype == 'package':
            return md5(name).digest(), None
        else:
            return None

    def make_key(self, key):
        return md5(key).digest()


class ReleaseIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '16s'
        super(ReleaseIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        name = data.get('name')
        datatype = data.get('type')
        if name is not None and datatype == 'release':
            return md5(name).digest(), None
        else:
            return None

    def make_key(self, key):
        return md5(key).digest()


class ReleaseByPackageIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '16s'
        super(ReleaseByPackageIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        package = data.get('package')
        datatype = data.get('type')
        if package is not None and datatype == 'release':
            return md5(package).digest(), None
        else:
            None

    def make_key(self, key):
        return md5(key).digest()


INDEXES = (
    ('package', PackageIndex),
    ('release', ReleaseIndex),
    ('rel_release_package', ReleaseByPackageIndex),
)
