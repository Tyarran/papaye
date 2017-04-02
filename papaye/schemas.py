import colander

from docutils.core import publish_parts
from deform.widget import PasswordWidget


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


class NullableMapping(colander.Mapping):

    def serialize(self, node, appstruct):
        if appstruct is None or appstruct == {}:
            return colander.null
        return super(NullableMapping, self).serialize(node, appstruct)

    def deserialize(self, node, cstruct):
        if cstruct == colander.null or cstruct == {}:
            return None
        return super(NullableMapping, self).deserialize(node, cstruct)


class APIDescription(colander.MappingSchema):
    content = colander.SchemaNode(colander.String(), missing=None)
    html = colander.SchemaNode(colander.Boolean())


class ReleaseFile(colander.MappingSchema):
    filename = colander.SchemaNode(colander.String())
    version = colander.SchemaNode(colander.String())
    upload_date = colander.SchemaNode(colander.String())
    size = colander.SchemaNode(colander.String())
    url = colander.SchemaNode(colander.String())


class APIOtherRelease(colander.MappingSchema):
    url = colander.SchemaNode(colander.String())
    version = colander.SchemaNode(colander.String())


class APIOtherReleases(colander.SequenceSchema):
    other_releases = APIOtherRelease()


class APIReleaseFiles(colander.SequenceSchema):
    release_files = ReleaseFile()


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
    description = APIDescription(typ=NullableMapping(), missing=None)
    platform = colander.SchemaNode(String(), missing=None)
    classifiers = colander.SchemaNode(Classifiers(), default=[])
    name = colander.SchemaNode(String(), missing=None)


def username_validator(node, value):
    request = node.bindings['request']
    usernames = [user.username for user in list(request.root)]
    if value not in usernames:
        raise colander.Invalid(node, 'Invalid username or password')
    node.bindings['user'] = request.root[value]
    node.data = value


class LoginSchema(colander.MappingSchema):
    username = colander.SchemaNode(String(), missing=None,
                                   validator=username_validator)
    password = colander.SchemaNode(
        String(), missing=None, widget=PasswordWidget()
    )

    def validator(self, node, appstruct):
        request = node.bindings['request']
        username = appstruct.get('username') or ''
        password = appstruct.get('password') or ''
        error = colander.Invalid(node, 'username and/or password invalid')
        username_matching_users = [
            user for user in request.root
            if user.username == username
        ]
        if not len(username_matching_users):
            raise error
        user = username_matching_users[0]
        if not user.password_verify(password):
            raise error
