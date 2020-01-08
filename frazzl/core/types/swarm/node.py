import sys
from multiprocessing import set_start_method

from frazzl.core.exceptions import ConfigError
from frazzl.core.types.app import Frazzl
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
        return self.context.process.is_alive()

    def start(self):
        self.context.process.start()

    def stop(self):
        self.context.process.terminate()

    def join(self):
        self.context.process.join()

    @classmethod
    def validate(cls, definition):
        node_name = definition.get("node_name")
        settings = definition.get("settings", None)
        if not settings:
            raise ConfigError(f"The node definition for {node_name} must specify the settings field.")

        port = settings.get("port", None)
        if not port:
            raise ConfigError(f"The settings for {node_name} must specify the port field.")

        return {"settings": settings}


class AppNode(LocalNode):
    def build(cls, context):
        # context.app
        # self.process = Process(target=start_app, args=[self.app])
        pass

    @classmethod
    def validate(cls, definition):
        node_name = definition.get("name")
        local_node_context = LocalNode.validate(definition)

        namespace = definition.get("namespace", None)
        if not namespace:
            raise ConfigError(f"The node definition for {node_name} must specify the namespace field.")

        hashed_app_name = get_hashed_app_name(node_name)
        __import__(namespace)
        app = getattr(sys.modules["__main__"], hashed_app_name, None)
        if app and isinstance(app, Frazzl):
            local_node_context.update({"app": app})
            return local_node_context

        raise ConfigError(f"Could not find an app named {node_name} in the namespace {namespace}.")
