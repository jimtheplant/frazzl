import atexit
import sys
import uuid
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec

import uvicorn
from ariadne.asgi import GraphQL

from frazzl.core.exceptions import ConfigError
from frazzl.core.types.config import AppConfig


class Frazzl:
    def __init__(self, name, config: AppConfig = None, schema=None, types=None):
        if not config and not schema and not types:
            raise ConfigError("Frazzl app must have a config object, or pass a schema and types")
        if not config and (not types or not schema):
            raise ConfigError("Frazzl app must have a config object, or pass a schema and types")
        elif not config and schema and types:
            config = AppConfig()
            config.schema = schema
            config.types = types
        self.config = config
        self.name = name
        self._graphql_types = {}

    def start(self):
        self.config.startup()
        temp_mod_name = str(uuid.uuid4().hex)
        spec = ModuleSpec(temp_mod_name, None)
        mod = module_from_spec(spec)
        mod._app = GraphQL(self.config._create_schema())
        sys.modules[temp_mod_name] = mod
        atexit.register(self.stop)
        uvicorn.run(temp_mod_name + ":_app", port=self.config.port if self.config.port else 8000)

    def stop(self):
        print("stopping")
        self.config.teardown()

    def __overwrite_config(self, attr, value):
        setattr(self.config, attr, value)
