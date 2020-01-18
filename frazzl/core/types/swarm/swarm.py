import atexit
import contextlib

import yaml

from frazzl.core.exceptions import ConfigError
from .gateway import GatewayNode
from .node import *
from .settings import SwarmSettings


class FrazzlSwarm:
    def __init__(self, swarm_definition):
        self.nodes = {}
        self.gateway_node = None
        self.settings = None
        self.swarm_definition = swarm_definition

    def build(self):
        self._build_nodes()
        return self

    @classmethod
    @contextlib.contextmanager
    def start_swarm(cls, definition, rebuild=False):
        swarm = FrazzlSwarm(definition)
        swarm.build()
        yield swarm
        if rebuild:
            swarm.build()
        swarm.start_nodes()

    def start_nodes(self):
        for node in self.nodes.values():
            node.start()
        self.gateway.start()
        atexit.register(self.stop)
        for node in self.nodes.values():
            node.context.process.join()

    @classmethod
    def validate(cls, swarm_definition):
        return cls._validate(swarm_definition)

    def _build_nodes(self):
        for key, value in self.swarm_definition.items():
            if key == "settings":
                self.settings = SwarmSettings.build(value)
            elif key == "gateway":
                continue
            else:
                self._build_node(key, value)
        gateway_definition = self.swarm_definition.get("gateway")
        self.gateway = GatewayNode.build(dict(name="gateway", **gateway_definition), nodes=self.nodes)

    def _build_node(self, node_name, node_definition):
        if "namespace" in node_definition.keys():
            self.nodes[node_name] = AppNode.build(dict(name=node_name, **node_definition))

    @classmethod
    def swarm_definition_from_yaml(cls, filename):
        try:
            with open(filename) as swarm_file:
                swarm_definition = yaml.load(swarm_file, yaml.BaseLoader)
        except FileNotFoundError:
            raise ConfigError(f"Swarm file {filename} was not found")
        return swarm_definition

    @classmethod
    def _validate(cls, swarm_definition):
        settings = None
        gateway = None
        nodes = {}
        for key, value in swarm_definition.items():
            if key == "settings":
                settings = SwarmSettings.validate(value)
            elif key == "gateway":
                gateway = GatewayNode.validate(dict(name=key, **value))
            else:
                nodes[key] = cls.validate_node(key, value)
        return {"settings": settings, "gateway": gateway, "nodes": nodes}

    @classmethod
    def validate_node(cls, node_name, node_definition):
        if "namespace" in node_definition.keys():
            node_context = AppNode.validate(dict(name=node_name, **node_definition))
            return node_context

        raise ConfigError(f"The node {node_name} did not match a definition for any supported nodes.")

    def stop(self):
        for node in self.nodes.values():
            node.stop()
            if isinstance(node, LocalNode):
                node.process.join()
