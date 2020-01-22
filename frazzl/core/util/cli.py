import yaml

from frazzl.core.constants import DEFAULT_SWARM


def update_default_frazzl_file(definition=DEFAULT_SWARM):
    with open(".frazzl", "w") as f:
        yaml.dump(definition, stream=f)
