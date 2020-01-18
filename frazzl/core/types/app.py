import sys
import uuid
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec

import uvicorn

from frazzl.core.exceptions import ConfigError
from frazzl.core.frazzl_asgi import FrazzlGQL
from frazzl.core.types.config import AppConfig
from frazzl.core.util.swarm import get_hashed_app_name


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
        setattr(sys.modules['__main__'], get_hashed_app_name(name), self)

    def start(self):
        self.config.startup()

    def stop(self):
        self.config.teardown()

    def __overwrite_config(self, attr, value):
        setattr(self.config, attr, value)

    def __str__(self):
        return self.config.schema


def start_app(app, port):
    temp_mod_name = str(uuid.uuid4().hex)
    spec = ModuleSpec(temp_mod_name, None)
    mod = module_from_spec(spec)
    mod._app = FrazzlGQL(app.config._create_schema(), app.start, app.stop)
    sys.modules[temp_mod_name] = mod
    uvicorn.run(temp_mod_name + ":_app", port=port)
