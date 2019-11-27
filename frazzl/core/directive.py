from typing import Union

from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLField, GraphQLObjectType, GraphQLInterfaceType


class KeyDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType):
        key_field = self.args["fields"]
        if object_.fields.get(key_field) is None:
            raise TypeError

    def visit_interface(self, iface: GraphQLInterfaceType):
        key_field = self.args["fields"]
        iface.fields.get(key_field)


class RequiresDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
            self,
            field: GraphQLField,
            object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ):
        pass


class ProvidesDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
            self,
            field: GraphQLField,
            object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ):
        pass


class ExternalDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
            self,
            field: GraphQLField,
            object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ):
        pass


class ExtendsDirective(SchemaDirectiveVisitor):
    def visit_interface(self, iface: GraphQLInterfaceType):
        pass

    def visit_object(self, object_: GraphQLObjectType):
        pass


FEDERATION_TYPES = {
    "key": KeyDirective,
    "requires": RequiresDirective,
    "provides": ProvidesDirective,
    "external": ExternalDirective,
    "extends": ExtendsDirective
}