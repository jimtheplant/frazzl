import sys
import os
import site
import subprocess

LAUNCHED_SERVICES = []
federation = []
GATEWAY_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "gateway")

class ServiceTypes:
    EXTERNAL = "external"
    MODULE = "module"
    LOCAL = "local"


def print_info(config):
    global federation
    service_name = config.APP_SERVICE.service_name
    print("Starting {0}".format(service_name))
    if len(federation) > 0:
        print("{0}'s federation is: ".format(service_name))
        for service_config in federation:
            service_type = service_config["type"]
            if service_type is ServiceTypes.LOCAL:
                federation_info = ServiceTypes.LOCAL + " at port " + str(service_config["port"]) + " using module: " + service_config["module_name"]
            elif service_type is ServiceTypes.EXTERNAL:
                federation_info = ServiceTypes.EXTERNAL + " at " + service_config["url"]
            elif service_type is ServiceTypes.MODULE:
                federation_info = ServiceTypes.MODULE
            else:
                raise Exception()
            print("\t\u2022 {0} ({1})".format(service_config["service_name"], federation_info))


def start_local(service_config):
    local_service = __import__(service_config["module_name"])
    subprocess.Popen([sys.executable, local_service.app.__file__], stdout=sys.stdout, stderr=sys.stderr)


def start_gateway():
    if os.name == "nt":
        activate_script = "activate.bat"
    else:
        activate_script = "activate"
    activate_cmd = os.path.join(GATEWAY_PATH, "node", "Scripts", activate_script)
    subprocess.Popen([activate_cmd] + " & node -v".split(), cwd=GATEWAY_PATH, stdout=sys.stdout, stderr=sys.stderr)


def start_services(config):
    global federation
    federation = config.FEDERATION
    print_info(config)
    if len(federation) > 0:
        for service_config in federation:
            service_type = service_config["type"]
            if service_type is ServiceTypes.LOCAL:
                start_local(service_config)
            elif service_type is ServiceTypes.EXTERNAL:
                pass
            elif service_type is ServiceTypes.MODULE:
                pass
            else:
                raise Exception()
    config.APP_SERVICE.start_service()




