from frazzl.core.constants import DEFAULT_NODE_DEFS, DEFAULT_SUBMODULES_PATHS


def start_swarm(nodes):
    pass


def make_swarm_definition(gateway, modules):
    port = 8000
    node_definitions = {}
    for module in modules:
        node_definition = dict(kv for kv in DEFAULT_NODE_DEFS.get("appNode").items())
        node_definition["module"] = module
        node_definition["port"] = port
        node_definitions[module] = node_definition
        port += 1
    gateway_definition = dict(kv for kv in DEFAULT_NODE_DEFS.get("gateway").items())
    gateway_definition["nodes"] = modules
    settings = {"gateway": str(gateway), "submodules": DEFAULT_SUBMODULES_PATHS}
    return {"settings": settings, "nodes": node_definitions, "gateway": gateway_definition}
