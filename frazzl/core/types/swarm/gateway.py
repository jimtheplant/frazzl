from multiprocessing import Process

from frazzl.core.exceptions import ConfigError
from frazzl.core.util.gateway import start_gateway, create_tempfile
from .node import FrazzlNode


class GatewayNode(FrazzlNode):
    def is_alive(self):
        return self.context.process and self.context.process.is_alive()

    def start(self):
        if self.context.process:
            self.context.process.start()

    def stop(self):
        if self.context.process:
            self.context.process.terminate()

    @classmethod
    def build(cls, context, nodes=None):
        if not context.local:
            return context
        temp_file_path = create_tempfile(nodes)
        context.process = Process(target=start_gateway, args=[temp_file_path])
        return context

    @classmethod
    def validate(cls, definition):
        local = False if definition.get("local", None) in ['false', 'f', 'False'] else True
        nodes = definition.get("nodes", None)
        if local and not nodes:
            raise ConfigError(
                "A local Gateway node was defined with no nodes and. The gateway must have at least one node."
            )
        if nodes and type(nodes) is not list:
            raise ConfigError(f"Error parsing gateway node definition. Got {nodes}")
        return {"local": local, "nodes": nodes}
