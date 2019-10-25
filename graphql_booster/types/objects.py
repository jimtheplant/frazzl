from ariadne import ObjectType

__OBJECT_TYPES = {}


def create_ariadne_type(name):
    if not __OBJECT_TYPES.get(name):
        __OBJECT_TYPES[name] = ObjectType(name)
    return __OBJECT_TYPES[name]


def __gql_object(_name, cls):
    class __ObjectType(cls):
        gql_type = create_ariadne_type(_name)
    return __ObjectType


def gql_object(name):
    def _gql_object(cls):
        return __gql_object(name, cls)
    return _gql_object


def create_object_type(name):
    created_class = __gql_object(name, _ObjectType)
    return created_class


class _ObjectType:
    gql_type = None

    def __init__(self):
        self.__bind_resolvers()

    def __bind_resolvers(self):
        def field_resolver(_resolver):
            def _field_resolver(info, *args, **kwargs):
                return _resolver(self, info, *args, **kwargs)
            return _field_resolver

        for field, resolver in self.gql_type._resolvers.items():
            setattr(self, field, field_resolver(resolver))

    @classmethod
    def field(cls, name):
        return cls.gql_type.field(name)

    @classmethod
    def set_field(cls, name, resolver):
        return cls.gql_type.set_field(name, resolver)

    @classmethod
    def set_alias(cls, name, to):
        return cls.gql_type.set_field(name, to)



