from multiprocessing import Process

from frazzl.core.exceptions import ConfigError
from frazzl.core.util.class_defs import validate_class
from frazzl.core.util.gateway import create_tempfile, start_gateway
from .node import FrazzlNode


@validate_class
class GatewayNode(FrazzlNode):
    required_fields = ["port", "nodes"]
    config_typename = "gateway"

    def __init__(self, nodes):
        super(GatewayNode, self).__init__()
        self.process = None
        self.port = None
        self.nodes_keys = []
        self.tempfile_path = None
        self.nodes = nodes

    def load(self, definition):
        super(GatewayNode, self).load(definition)
        self.nodes_keys = definition.get("nodes")
        self.tempfile_path = create_tempfile(self.nodes)
        self.process = Process(target=start_gateway, args=(self.tempfile_path,))
        self.url = "http://localhost:4000"

    def start(self):
        self.process.start()

    def is_alive(self):
        self.process.is_alive()

    @classmethod
    def validate(cls, definition):
        nodes = definition.get("nodes")
        if type(nodes) is not list:
            ConfigError("The gateway definition must have a list of nodes.")
        return {"nodes": nodes}
