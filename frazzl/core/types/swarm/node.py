from importlib import import_module
from multiprocessing import Process
from time import sleep

from frazzl.core.exceptions import ConfigError
from frazzl.core.types.app import Frazzl, start_app_proc_target
from frazzl.core.types.config import AppConfig
from frazzl.core.types.swarm.settings import Modules
from frazzl.core.util.class_defs import WithContext


class FrazzlNode(WithContext):
    config_typename = None

    def __init__(self, definition, settings):
        super(FrazzlNode, self).__init__()
        self.settings = settings
        self.context = {"settings": settings}
        self.context = FrazzlNode.validate(definition, self.context)

    def load(self):
        raise NotImplementedError

    def is_alive(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    @classmethod
    def validate(cls, definition, context):
        node_type = definition.get("type", None)
        if node_type is None:
            raise ConfigError(f"All nodes must define a type. Got: {definition} that has no type")
        return {"type": node_type}


class LocalNode(FrazzlNode):

    def __init__(self, definition, settings):
        super(LocalNode, self).__init__(definition, settings)
        self.process = None
        self.app = None
        self.context = LocalNode.validate(definition, self.context)

    def load(self):
        raise NotImplementedError

    def is_alive(self):
        return self.process.is_alive()

    def start(self):
        self.process.start()
        print(self.process.pid)
        sleep(5)
        self.stop()

    def stop(self):
        self.process.terminate()


    @classmethod
    def validate(cls, definition, context):
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

        modules_setting = context.settings[Modules.setting_name]
        submodules = modules_setting.search_submodules(module)
        return {"modules": submodules + [module], "port": port, "url": f"http://localhost:{port}/"}


class AppModuleNode(LocalNode):
    config_typename = "appNode"

    def __init__(self, definition, settings):
        super(AppModuleNode, self).__init__(definition, settings)
        self.context = AppModuleNode.validate(definition, self.context)

    def load(self):
        self.app = self.context.app
        self.process = Process(target=start_app_proc_target, args=[self.app])

    @classmethod
    def validate(cls, definition, context):
        app_name = definition.get("app", None)
        if not app_name:
            raise ConfigError(f"The {cls.config_typename} definition must specify the app_name field. "
                              f"None were found.")

        for submodule in context.modules:
            app = getattr(submodule, app_name, None)
            if app and isinstance(app, Frazzl):
                return {"app": app}

        raise ConfigError(f"Could not find have a valid config object named {app_name}. Modules searched:"
                          f"{[module.__name__ for module in context.modules]}")


class ConfigNode(LocalNode):
    config_typename = "configNode"

    def __init__(self, definition, settings):
        super(ConfigNode, self).__init__(definition, settings)
        self.config_obj = None
        self.context = ConfigNode.validate(definition, self.context)

    def load(self):
        config_type = self.context.config
        self.config_obj = config_type()
        self.app = Frazzl(str(id(self)), config=self.config_obj)
        self.process = Process(target=start_app_proc_target, args=[self.app])

    @classmethod
    def validate(cls, definition, context):
        config_name = definition.get("config", None)
        if not config_name:
            raise ConfigError(f"The {cls.config_typename} definition must specify the app_name field. "
                              f"None were found.")

        for submodule in context.modules:
            config = getattr(submodule, config_name, None)
            if config and issubclass(config, AppConfig):
                return {"config": config}

        raise ConfigError(f"Could not find have a valid config object named {config_name}. Modules searched:"
                          f"{[module.__name__ for module in context.modules]}")
