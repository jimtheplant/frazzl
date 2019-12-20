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

    def stop(self):
        self.config.teardown()

    def __overwrite_config(self, attr, value):
        setattr(self.config, attr, value)


def start_app_proc_target(app, error_event, barier):
    try:
        start_app(app)
    finally:
        error_event.acquire()
        error_event.notify_all()
        error_event.release()


def start_app(app):
    temp_mod_name = str(uuid.uuid4().hex)
    spec = ModuleSpec(temp_mod_name, None)
    mod = module_from_spec(None)
    mod._app = GraphQL(app.config._create_schema())
    sys.modules[temp_mod_name] = mod
    uvicorn.run(temp_mod_name + ":_app", port=app.config.port if app.config.port else 8000)
