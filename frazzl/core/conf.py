import uvicorn
from ariadne import make_executable_schema

from frazzl.core.directive import FEDERATION_TYPES
from frazzl.core.federation_spec import SERVICE_TEMPLATE, ENTITY_QUERY, make_template

class AppConfig:
    schema = None
    types = None
    port = 8000

    def startup(self):
        pass

    def _create_schema(self):
        schema = self.schema
        bindables = self.types
        directives = {}.update(FEDERATION_TYPES)

        type_defs = make_template(schema)

        return make_executable_schema(type_defs, bindables=bindables, directives=directives)

    def teardown(self):
        pass
