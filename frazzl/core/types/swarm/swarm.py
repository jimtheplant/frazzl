import atexit

import yaml

from .gateway import GatewayNode
from .node import *
from .settings import SwarmSettings


class FrazzlSwarm:
    default_node_types = [ConfigNode, AppModuleNode]
    gateway_node_type = GatewayNode
    __all_node_types = [ConfigNode, AppModuleNode, GatewayNode, LocalNode, FrazzlNode]

    def __init__(self, node_types: list = None):
        self.gateway_node = None
        self.swarm_definition = None
        self.swarm_settings = None
        self.nodes = None
        self.node_types = dict((node_type.config_typename, node_type)
                               for node_type in self.default_node_types)
        if node_types:
            self.node_types.update(dict((node_type.config_typename, node_type) for node_type in node_types))

        self.processes = []

    def load_swarm(self, swarm_definition):
        if type(swarm_definition) is dict:
            self.swarm_definition = swarm_definition
        else:
            with open(swarm_definition) as swarm_file:
                self.swarm_definition = yaml.load(swarm_file, yaml.BaseLoader)
        self.nodes = self.validate(self.swarm_definition)
        self.load_nodes()
        if self.gateway_node:
            self.gateway_node.load()

    def load_nodes(self):
        for node in self.nodes.values():
            node.load()
            if isinstance(node, LocalNode):
                self.processes.append(node.process)

    def validate(self, swarm_definition):
        settings = SwarmSettings.validate(swarm_definition.get("settings", None))

        if not swarm_definition.get("gateway") and settings.gateway:
            raise ConfigError("A swarm must have a gateway attribute in it's definition.")
        if not swarm_definition.get("nodes"):
            raise ConfigError("A swarm must have a nodes attribute in it's definition.")

        nodes = {}
        node_definitions = swarm_definition.get("nodes")
        for node_name, node_definition in node_definitions.items():
            if type(node_definition) is not dict:
                raise ConfigError(f"{node_name} has an incorrect node definition.")

            node_typename = node_definition.get("type")
            if node_definition.get("type") is None:
                raise ConfigError(f"{node_name} has an incorrect node definition. "
                                  "Every node must have a type attribute. "
                                  f"Got: {node_definition}")
            node_type = self.node_types.get(node_typename)
            node = node_type(node_definition, settings)
            nodes[node_name] = node

        if settings.gateway:
            self.gateway_node = self.gateway_node_type(swarm_definition.get("gateway"), settings, nodes)

        return nodes

    def start_swarm(self):

        for node in self.nodes.values():
            node.start()

        if self.gateway_node:
            self.gateway_node.start()

        atexit.register(self.stop)
        for proc in self.processes:
            proc.join()

    def nodes_ready(self):
        for node in self.nodes.values():
            if not node.is_alive():
                return False
        return True

    def ready(self):
        return (not self.gateway_node or self.gateway_node.is_alive()) and self.nodes_ready()

    def stop(self):
        for node in self.nodes.values():
            node.stop()
            if isinstance(node, LocalNode):
                node.process.join()
