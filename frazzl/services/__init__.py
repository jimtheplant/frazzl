import os
import sys
import importlib

SERVICES_DIR = os.path.dirname(__file__)

def init_services():
    for service in os.listdir(SERVICES_DIR):
        service_dir = os.path.join(SERVICES_DIR, service)
        if os.path.isdir(service_dir):
            sys.path.append(service_dir)
            importlib.import_module(service)
