import atexit

import yaml

from .gateway import GatewayNode
from .node import *
from .settings import SwarmSettings


class FrazzlSwarm:
    default_node_types = [AppNode]
    gateway_node_type = GatewayNode
    __all_node_types = [AppNode, GatewayNode, LocalNode, FrazzlNode]

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

    def __str__(self):
        nodes_str = ""
        for node in self.nodes.values():
            nodes_str += str(node)
        return nodes_str

    @classmethod
    def swarm_definition_from_yaml(cls, filename):
        try:
            with open(filename) as swarm_file:
                swarm_definition = yaml.load(swarm_file, yaml.BaseLoader)
        except FileNotFoundError:
            raise ConfigError(f"Swarm file {filename}, was not found")
        except RuntimeError:
            raise ConfigError(f"Error reading swarm file {filename}")

        return swarm_definition

    def load_swarm(self, swarm_definition):
        if type(swarm_definition) is dict:
            self.swarm_definition = swarm_definition
        else:
            with open(swarm_definition) as swarm_file:
                self.swarm_definition = yaml.load(swarm_file, yaml.BaseLoader)
        swarm_prototype = self.validate(self.swarm_definition)
        self.nodes = swarm_prototype["nodes"]
        self.swarm_settings = swarm_prototype["settings"]
        self.load_nodes()
        if self.gateway_node:
            self.gateway_node.load()

    def load_nodes(self):
        for node in self.nodes.values():
            node.load()
            if isinstance(node, LocalNode):
                self.processes.append(node.process)

    @classmethod
    def validate(cls, swarm_definition):
        settings = None
        gateway = None
        nodes = {}
        for key, value in swarm_definition.items():
            if key == "settings":
                settings = SwarmSettings.validate(value)
                swarm_setting = SwarmSettings.build(value)
            elif key == "gateway":
                gateway = GatewayNode.validate(dict(name=key, **value))
            else:
                nodes[key] = cls.validate_node(key, value)
        return {"settings": settings, "gateway": gateway, "nodes": nodes}

    @classmethod
    def validate_node(cls, node_name, node_definition):
        if "namespace" in node_definition.keys():
            node = AppNode.validate(dict(name=node_name, **node_definition))
            return node

        raise ConfigError(f"The node {node_name} did not match a definition for any supported nodes.")

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
