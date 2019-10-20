from ariadne import ObjectType


class Entity:
    pass


def create_entity(name, key_resolvers):
    object_type = ObjectType(name)
    setattr(object_type, "key_resolver", key_resolvers)
    return object_type
