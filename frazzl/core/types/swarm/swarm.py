import yaml

from .gateway import GatewayNode
from .node import *
from .settings import SwarmSettings


class FrazzlSwarm:
    default_node_types = [ConfigNode, AppModuleNode]
    gateway_node_type = GatewayNode
    __all_node_types = [ConfigNode, AppModuleNode, GatewayNode, LocalNode, FrazzlNode]

    def __init__(self, node_types: dict = None):
        self.nodes = {}
        self.gateway_node = None
        self.swarm_definition = None
        self.swarm_settings = None
        self.node_types = dict((_type.config_typename, _type) for _type in self.default_node_types)
        if node_types:
            self.node_types.update(node_types)

    def load_swarm(self, swarm_definition):
        if type(swarm_definition) is dict:
            self.swarm_definition = swarm_definition
        else:
            with open(swarm_definition) as swarm_file:
                self.swarm_definition = yaml.load(swarm_file, yaml.BaseLoader)
        self.validate(self.swarm_definition)
        node_definitions = self.swarm_definition.get("nodes")
        self.load_nodes(node_definitions)
        gateway_definition = self.swarm_definition.get("gateway")
        self.load_gateway(gateway_definition)

    def load_gateway(self, gateway_definition):
        self.gateway_node = self.gateway_node_type(list(self.nodes.values()))
        self.gateway_node.load(gateway_definition)

    def load_nodes(self, node_definitions):
        for node_name, node_definition in node_definitions.items():
            node = self.load_node(node_name, node_definition)
            self.nodes[node_name] = node

    @classmethod
    def validate(cls, swarm_definition):
        if not swarm_definition.get("gateway"):
            raise ConfigError("A swarm must have a gateway attribute in it's definition.")
        if not swarm_definition.get("nodes"):
            raise ConfigError("A swarm must have a nodes attribute in it's definition.")

        settings = SwarmSettings.validate(swarm_definition)
        node_definitions = swarm_definition.get("nodes")
        node_types = dict((_type.config_typename, _type) for _type in cls.default_node_types + [GatewayNode])
        for node_type in cls.__all_node_types:
            node_type.context["settings"] = settings
        for node_name, node_definition in node_definitions.items():
            if type(node_definition) is not dict:
                raise ConfigError(f"{node_name} has an incorrect node definition.")
            if node_definition.get("type") is None:
                raise ConfigError(f"{node_name} has an incorrect node definition. "
                                  "Every node must have a type attribute. "
                                  f"Got: {node_definition}")
            node_typename = node_definition.get("type")
            node_type = node_types.get(node_typename)
            node_type.validate(node_definition)
        return {"settings": settings}

    def start_swarm(self):
        for node in self.nodes.values():
            node.start()

        while not self.nodes_ready():
            continue
        self.gateway_node.start()

    def nodes_ready(self):
        for node in self.nodes.values():
            if not node.is_alive():
                return False
        return True

    def ready(self):
        return self.gateway_node.is_alive() and self.nodes_ready()

    def load_node(self, node_name, node_definition):
        node_typename = node_definition.get("type")
        node_type = self.node_types.get(node_typename)
        node = node_type()
        node.load(node_definition)
        node.name = node_name
        return node
