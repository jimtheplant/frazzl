import json
import multiprocessing
import os
import subprocess
import sys
import tempfile

import uvicorn
from ariadne.asgi import GraphQL

LAUNCHED_SERVICES = []
federation = []
GATEWAY_PATH = os.path.join(os.path.dirname(__file__), "..", "gateway")


class ServiceTypes:
    SELF = "self"
    EXTERNAL = "external"
    MODULE = "module"
    LOCAL = "local"


def print_info(config):
    global federation
    service_name = config.CONFIG["service"]["service_name"]
    print("Starting {0}".format(service_name))
    if len(federation) > 0:
        print("{0}'s federation is: ".format(service_name))
        for service_config in federation:
            service_type = service_config["type"]
            if service_type is ServiceTypes.LOCAL:
                federation_info = ServiceTypes.LOCAL + " at port " + str(service_config["port"]) + " using module: " + \
                                  service_config["module_name"]
            elif service_type is ServiceTypes.EXTERNAL:
                federation_info = ServiceTypes.EXTERNAL + " at " + service_config["url"]
            elif service_type is ServiceTypes.MODULE:
                federation_info = ServiceTypes.MODULE
            else:
                raise Exception()
            print("\t\u2022 {0} ({1})".format(service_config["service_name"], federation_info))


def __start_service(service, port):
    schema = service.create_schema_from_template()
    app = GraphQL(schema)
    uvicorn.run(app, port=port)


def start_service(service, port):
    process = multiprocessing.Process(target=__start_service, args=(service, port))
    process.start()
    return process


def start_local(service_config):
    local_service = __import__(service_config["module_name"])
    return start_service(local_service.APP_SERVICE, int(service_config["port"]))


def create_tempfile(config):
    config_file = tempfile.mkstemp()
    apollo_config = {"federation": []}
    apollo_config["federation"].extend(config.CONFIG["federation"])
    apollo_config["federation"].append(config.CONFIG["service"])
    json.dump(apollo_config, open(config_file[1], "w"), ensure_ascii=False)
    return config_file[1]


def start_gateway(config):
    config_file_path = create_tempfile(config)
    start_commands = "node index.js start".split()
    process = subprocess.Popen(start_commands + [config_file_path], cwd=GATEWAY_PATH, stdout=sys.stdout,
                               stderr=sys.stderr)
    process.wait()


def start_services(config):
    global federation
    services = []
    federation = config.CONFIG["federation"]
    print_info(config)
    if len(federation) > 0:
        for service_config in federation:
            service_type = service_config["type"]
            if service_type is ServiceTypes.LOCAL:
                services.append(start_local(service_config))
            elif service_type is ServiceTypes.EXTERNAL:
                pass
            elif service_type is ServiceTypes.MODULE:
                pass
            else:
                raise Exception()
    services.append(start_service(config.APP_SERVICE, config.APP_PORT))
    start_gateway(config)
    for service in services:
        service.kill()
