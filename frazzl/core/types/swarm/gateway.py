from multiprocessing import Process

from frazzl.core.exceptions import ConfigError
from frazzl.core.util.gateway import create_tempfile, start_gateway
from .node import FrazzlNode


class GatewayNode(FrazzlNode):
    config_typename = "gateway"

    def __init__(self, definition, settings, nodes):
        super(GatewayNode, self).__init__(definition, settings)
        self.process = None
        self.nodes = nodes
        self.context = GatewayNode.validate(definition, self.context)

    def load(self):
        tempfile_path = create_tempfile(self.nodes)
        self.process = Process(target=start_gateway, args=(tempfile_path,))

    def start(self):
        self.process.start()

    def is_alive(self):
        self.process.is_alive()

    @classmethod
    def validate(cls, definition, context):
        nodes = definition.get("nodes")
        if type(nodes) is not list:
            ConfigError("The gateway definition must have a list of nodes.")
        return {}
