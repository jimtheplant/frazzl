from ariadne.asgi import GraphQL
import uvicorn
from frazzl.core.conf import AppConfig


class Frazzl:

    def __init__(self, name, config: AppConfig = None, schema=None, types=None):
        if not config and not schema and not types:
            raise ValueError()
        if not config and (not types or not schema):
            raise ValueError()
        elif not config and schema and types:
            config = AppConfig()
            config.schema = schema
            config.types = types
        self.config = config
        self.name = name

    def get_app(self):
        return GraphQL(self.config._create_schema())

    def start(self):
        self.config.startup()
        uvicorn.run(GraphQL(self.config._create_schema()), port=self.config.port if self.config.port else 8000)

    def stop(self):
        self.config.teardown()
        
    def __overwrite_config(self, attr, value):
        setattr(self.config, attr, value)


class AppLoader:
    def __init__(self):
        self.processes = []





