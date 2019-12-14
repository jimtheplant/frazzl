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

extend type Query {{
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

def __make_entity_str(entities):
    if len(entities) <= 0:
        return ""
    entity_names = list(entities.keys())
    union_str = "union _Entity = " + entity_names[0]
    for entity_name in entity_names[1:]:
        union_str += " | "
        union_str += entity_name
    return union_str


def make_template(schema):
    return SERVICE_TEMPLATE.format(union_entities="", entity_query="", query_str=schema)


def service_resolver(schema):
    def _service_resolver(*_):
        return {"sdl": schema}

    return _service_resolver
