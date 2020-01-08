from .node import FrazzlNode


class GatewayNode(FrazzlNode):
    config_typename = "gateway"

    def start(self):
        self.context.process.start()

    def is_alive(self):
        self.context.process.is_alive()

    @classmethod
    def build(cls, context):
        return {}

    @classmethod
    def validate(cls, definition):
        local = False if definition.get("local", None) in ['false', 'f', 'False'] else True
        return {"local": local}
