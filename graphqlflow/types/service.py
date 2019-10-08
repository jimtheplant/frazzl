from ariadne import ObjectType, QueryType, make_executable_schema, UnionType, gql
from .directive import *
from .scalars import _FieldSet, _Any
from ariadne.asgi import GraphQL
import uvicorn
import uuid

ENTITY_QUERY = "_entities(representations: [_Any!]!): [_Entity]!"
SERVICE_TEMPLATE = """
scalar _Any
scalar _FieldSet

# a union of all types that use the @key directive
{union_entities}

type _Service {{
  sdl: String
  name: String!
}}

{query_str}

{extend_query} type Query {{
  {entity_query}
  _service: _Service!
}}

directive @external on FIELD_DEFINITION
directive @requires(fields: _FieldSet!) on FIELD_DEFINITION
directive @provides(fields: _FieldSet!) on FIELD_DEFINITION
directive @key(fields: _FieldSet!) on OBJECT | INTERFACE

# this is an optional directive discussed below
directive @extends on OBJECT | INTERFACE
"""


class Service:
    gql_type = ObjectType("_Service")

    def __init__(self, service_name, schema, query=None, port=8000):
        self.service_name = service_name
        self.extend_query = "extend" if query else ""
        self.query = query if query else QueryType()
        self.directives = {"key": KeyDirective, "requires": RequiresDirective, "provides": ProvidesDirective,
                           "external": ExternalDirective, "extends": ExtendsDirective}
        self.sdl = schema
        self.entities = {}
        self.federation_types = [self.gql_type]
        self.query.set_field("_service", self.resolve_service)
        self.gql_type.set_field("sdl", self.resolve_sdl)
        self.gql_type.set_field("name", self.resolve_name)
        self.port = port

    def resolve_name(self, info, context):
        return self.service_name

    def resolve_service(self, info, context):
        return self.gql_type

    def resolve_sdl(self, info, context):
        return self.sdl

    def resolve_entities(self, obj, *_):
        return obj["__typename"]

    def _entities(self, *_, representations=None):
        rv = []
        for representation in representations:
            entity_type = self.entities[representation["__typename"]]
            key = {k: v for (k, v) in representation.items() if k != "__typename"}
            entity = entity_type.key_resolver(key)
            entity["__typename"] = representation["__typename"]
            rv.append(entity)
        return rv

    def create_schema_from_template(self):
        template = SERVICE_TEMPLATE
        entity_union_str = self._make_entity_str()
        entity_query_str = ""
        if entity_union_str != "":
            entity_union = UnionType("_Entity")
            entity_union.set_type_resolver(self.resolve_entities)
            self.query.set_field("_entities", self._entities)
            entity_query_str = ENTITY_QUERY
            self.federation_types.append(entity_union)
        template = template.format(union_entities=entity_union_str, entity_query=entity_query_str, query_str=self.sdl, extend_query=self.extend_query)
        return make_executable_schema(template, [self.query, _Any, _FieldSet] + [ObjectType(entity_name) for entity_name in self.entities.keys()] + self.federation_types,
                                      directives=self.directives)

    def start_service(self):
        schema = self.create_schema_from_template()
        app = GraphQL(schema)
        uvicorn.run(app, port=self.port)

    def _make_entity_str(self):
        if len(self.entities) <= 0:
            return ""
        entity_names = list(self.entities.keys())
        union_str = "union _Entity = " + entity_names[0]
        for entity_name in entity_names[1:]:
            union_str += " | "
            union_str += entity_name
        return union_str

    def add_entity(self, entity_type):
        self.entities[entity_type.name] = entity_type

