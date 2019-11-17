from ariadne import ObjectType


class Entity:
    pass


def create_entity(name, key_resolvers, key_name):
    object_type = ObjectType(name)
    setattr(object_type, "key_resolver", key_resolvers)
    object_type.set_field(key_name, key_resolvers)
    return object_type
