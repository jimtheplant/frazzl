import json
import os
import subprocess
import sys
import tempfile

GATEWAY_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "gateway")


def create_tempfile(nodes):
    config_file = tempfile.mkstemp()
    apollo_config = {"federation": [{"name": node_name, "url": node.context.url} for node_name, node in nodes.items()]}
    json.dump(apollo_config, open(config_file[1], "w"), ensure_ascii=False)
    return config_file[1]


def start_gateway(config_file_path):
    start_commands = "node index.js start".split()
    process = subprocess.Popen(start_commands + [config_file_path], cwd=GATEWAY_PATH, stdout=sys.stdout,
                               stderr=sys.stderr)
    process.wait()
