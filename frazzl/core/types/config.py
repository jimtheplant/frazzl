from ariadne import make_executable_schema, QueryType

from frazzl.core.federation.directive import FEDERATION_TYPES
from frazzl.core.federation.federation_spec import make_template, service_resolver


class AppConfig:
    schema = None
    types = None
    port = 8000

    def startup(self):
        pass

    def service_resolver(self, *_):
        return {"sdl": self.schema}

    def _create_schema(self):
        schema = self.schema
        bindables = self.types
        for bindable in bindables:
            if type(bindable) is QueryType:
                bindable.set_field("_service", service_resolver(self.schema))
        directives = {}.update(FEDERATION_TYPES)

        type_defs = make_template(schema)

        return make_executable_schema(type_defs, bindables=bindables, directives=directives)

    def teardown(self):
        pass
