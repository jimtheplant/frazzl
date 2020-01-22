import sys
from multiprocessing import set_start_method, Process

from frazzl.core.exceptions import ConfigError
from frazzl.core.types.app import Frazzl, start_app
from frazzl.core.util.class_defs import FrazzlBuilder
from frazzl.core.util.swarm import get_hashed_app_name

set_start_method("spawn")


class FrazzlNode(FrazzlBuilder):
    def is_alive(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    @classmethod
    def build(cls, context):
        return {}

    @classmethod
    def validate(cls, definition):
        return {}

    def __str__(self):
        return f"{self.context}"


class LocalNode(FrazzlNode):
    def is_alive(self):
        return self.process.is_alive()

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()

    def join(self):
        self.process.join()

    @classmethod
    def validate(cls, definition):
        node_name = definition.get("name")
        settings = definition.get("settings", None)
        if not settings:
            raise ConfigError(f"The node definition for {node_name} must specify the settings field.")

        port = settings.get("port", None)
        if not port:
            raise ConfigError(f"The settings for {node_name} must specify the port field.")
        try:
            port = int(port)
        except ValueError:
            raise ConfigError(f"Port given was not valid. Got: {port}")
        return {"settings": settings}


class AppNode(LocalNode):

    @classmethod
    def build(cls, context):
        port = context.settings.get("port", None)
        port = int(port)
        context.url = f"http://localhost:{port}"
        context.process = Process(target=start_app, args=[context.app, port])
        return context

    @classmethod
    def validate(cls, definition):
        node_name = definition.get("name")
        local_node_context = LocalNode.validate(definition)

        namespace = definition.get("namespace", None)
        if not namespace:
            raise ConfigError(f"The node definition for {node_name} must specify the namespace field.")

        hashed_app_name = get_hashed_app_name(node_name)
        try:
            __import__(namespace)
            app = getattr(sys.modules["__main__"], hashed_app_name, None)
            if app and isinstance(app, Frazzl):
                local_node_context.update({"app": app})
                return local_node_context
        except ModuleNotFoundError:
            raise ConfigError(f"Could not find an app named {node_name} in the namespace {namespace}.")
