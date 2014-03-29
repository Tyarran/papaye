from BTrees.OOBTree import OOBTree
from persistent import Persistent


class Package(Persistent):
    __parent__ = __name__ = None

    def __init__(self, name):
        self.__name__ = name
        self.releases = OOBTree()

    def __getitem__(self, release_name):
        return self.releases[release_name]


class Release(Persistent):
    __parent__ = __name__ = None

    def __init__(self, name, version):
        self.__name__ = name
        self.release_files = OOBTree()
        self.version = version

    def __getitem__(self, release_file_name):
        return self.release_files[release_file_name]


class ReleaseFile(Persistent):
    __parent__ = __name__ = None

    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

#import pickle

#from pyramid.registry import global_registry


#class CRUDMixin(object):

#    #def save(self):
#        #db_env = global_registry.db_env
#        #with db_env.begin(write=True) as db:
#            #db.put(self.name, pickle.dumps(self))

#    @classmethod
#    def get(cls, key):
#        """ Return a model object for given key"""
#        db_env = global_registry.db_env
#        with db_env.begin() as db:
#            return pickle.loads(db.get(key))

#    @classmethod
#    def get_many(cls, *args):
#        """ Return a generator for keys given in args"""
#        db_env = global_registry.db_env
#        with db_env.begin() as db:
#            for key in args:
#                yield pickle.loads(db.get(key))


#class Group(CRUDMixin, object):

#    def __init__(self, name, permissions, users=[]):
#        self.name = name
#        self.permissions = permissions
#        self.users = users
#        for user in users:
#            user.__group__ = self
#            self.users.append(user)


#class User(CRUDMixin, object):

#    def __init__(self, name, password):
#        self.name = name
#        self.password = password
