from ariadne import SchemaBindable
from graphql import GraphQLSchema


class FrazzlObject(SchemaBindable):

    def __init__(self, name):
        self.name = name
        self.resolvers = {}

    def bind_resolver(self, func, field):
        self.resolvers[field] = func

    def bind_to_schema(self, schema: GraphQLSchema):
        pass
