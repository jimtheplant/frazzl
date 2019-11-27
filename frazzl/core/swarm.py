from importlib import import_module
from .app import Frazzl
from .conf import AppConfig
from multiprocessing import Process


class FrazzlNode:
    frazzl_logger = None

    def load_app(self, load_context):
        raise NotImplementedError

    def is_alive(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError


class LocalNode(FrazzlNode):
    def __init__(self):
        super(LocalNode, self).__init__()
        self.process = None
        self.logger = None

    def load_app(self, load_context):
        logger = load_context.get("logger")
        if logger:
            self.logger = logger

    def is_alive(self):
        return self.process.is_alive

    def start(self):
        self.process.start()


class ModuleNode(LocalNode):

    def __init__(self):
        super(ModuleNode, self).__init__()

    def load_app(self, load_context):
        super(ModuleNode, self).load_app(load_context)
        module_name = load_context.get("module_name")
        if not module_name:
            raise ValueError

        module = import_module(module_name)
        if not module.app or type(module.app) is not Frazzl:
            raise ValueError
        app = module.app
        self.process = Process(target=app.start)


class ConfigNode(LocalNode):
    def __init__(self):
        super(ConfigNode, self).__init__()

    def load_app(self, load_context):
        app_config = load_context.get("app_config")
        if not app_config or not isinstance(app_config, AppConfig):
            raise ValueError

        app = Frazzl(str(id(self)), config=app_config)
        self.process = Process(target=app.start)


class FrazzlSwarm:
    def __init__(self):
        self.nodes = []
        self.gateway_process = None

    def ready(self):
        for node in self.nodes:
            if not node.is_alive():
                return False
        return self.gateway_process.is_alive()
