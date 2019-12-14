from importlib import import_module
from multiprocessing import Process

from frazzl.core.exceptions import ConfigError
from frazzl.core.types.app import Frazzl
from frazzl.core.types.config import AppConfig
from frazzl.core.util.class_defs import validate_class


@validate_class
class FrazzlNode:
    config_typename = None
    required_fields = ["type"]
    frazzl_logger = None

    def __init__(self):
        self.url = None
        self.name = None

    def load(self, definition):
        self.__class__.validate(definition)

    def is_alive(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    @classmethod
    def validate(cls, definition):
        node_type = definition.get("type", None)
        if node_type is None:
            raise ConfigError(f"All nodes must define a type. Got: {definition} that has no type")
        return {"type": node_type}


@validate_class
class LocalNode(FrazzlNode):
    required_fields = ["module", "port"]
    search_modules = ["app", "config"]

    def __init__(self):
        super(LocalNode, self).__init__()
        self.process = None
        self.logger = None
        self.module = None
        self.port = None

    def load(self, definition):
        super(LocalNode, self).load(definition)
        logger = definition.get("logger")
        if logger:
            self.logger = logger

        self.module = import_module(definition.get("module"))
        self.port = definition.get("port")
        self.url = f"http://localhost:{self.port}/"

    def is_alive(self):
        return self.process.is_alive()

    def start(self):
        self.process.start()

    @classmethod
    def validate(cls, definition):
        module_name = definition.get("module")
        if not module_name:
            raise ConfigError("No module present in the definition.")
        try:
            module = import_module(module_name)
        except ImportError:
            raise ConfigError(f"Module {module_name} was not found")
        port = definition.get("port")
        if not port:
            raise ConfigError("All local nodes must define a port.")
        try:
            port = int(port)
        except ValueError:
            raise ConfigError("All local nodes must define a port as a valid integer.")
        submodule_settings = cls.context["settings"]["submodules"]
        submodules = submodule_settings.search_submodules(module)
        return {"module": module, "port": port, "submodules": submodules}


@validate_class
class AppModuleNode(LocalNode):
    config_typename = "app_node"
    required_fields = ["app"]

    def __init__(self):
        super(AppModuleNode, self).__init__()

    def load(self, definition):
        super(AppModuleNode, self).load(definition)
        app = self.context["app"]
        self.process = Process(target=app.start)

    @classmethod
    def validate(cls, definition):
        module = cls.context["module"]
        app_name = definition.get("app", "")
        submodules = cls.context.get("submodules", [])
        modules_to_search = list(submodules.values()) + [module]
        for submodule in modules_to_search:
            app = getattr(submodule, app_name, None)
            if app and isinstance(app, Frazzl):
                return {"app": app}

        raise ConfigError(f"Could not find have a valid config object named {app_name}. Modules searched:"
                          f"{[module.__name__ for module in modules_to_search]}")


@validate_class
class ConfigNode(LocalNode):
    config_typename = "config_node"
    required_fields = ["config"]

    def __init__(self):
        super(ConfigNode, self).__init__()
        self.config_obj = None

    def load(self, definition):
        super(ConfigNode, self).load(definition)
        config_type = self.context.get("config")
        self.config_obj = config_type()
        app = Frazzl(str(id(self)), config=self.config_obj)
        self.process = Process(target=app.start)

    @classmethod
    def validate(cls, definition):
        module = cls.context["module"]
        config_name = definition.get("config", "")
        submodules = cls.context.get("submodules", [])
        modules_to_search = list(submodules.values()) + [module]
        for submodule in modules_to_search:
            config = getattr(submodule, config_name, None)
            if config and issubclass(config, AppConfig):
                return {"config": config}

        raise ConfigError(f"Could not find have a valid config object named {config_name}. Modules searched:"
                          f"{[module.__name__ for module in modules_to_search]}")
