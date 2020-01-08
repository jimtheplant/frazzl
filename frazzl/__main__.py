import os
import subprocess

import click
import yaml


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org:null', '')


yaml.add_representer(type(None), represent_none)

from frazzl.core.constants import VERSION, DEFAULT_SWARM
from frazzl.core.types.swarm.swarm import FrazzlSwarm
from frazzl.core.exceptions import ConfigError


@click.group()
@click.version_option(version=VERSION)
@click.option("--swarm-config", "-c", type=click.Path(), default="frazzl-swarm.yaml")
@click.pass_context
def cli(ctx, swarm_config):
    swarm_definition = {}
    try:
        swarm_definition = FrazzlSwarm.swarm_definition_from_yaml(".frazzl")
    except ConfigError:
        pass
    except FileNotFoundError:
        pass
    swarm_definition.update(FrazzlSwarm.swarm_definition_from_yaml(swarm_config))
    ctx.obj = {"swarm_definition": swarm_definition}


@cli.command()
def init():
    gateway_path = os.path.join(os.path.dirname(__file__), "gateway")
    subprocess.run("nodeenv -p".split())
    subprocess.run("npm install", cwd=gateway_path, shell=True)
    update()


@cli.group()
def config():
    pass


@config.command()
def ls():
    pass


@config.command()
def update():
    with open(".frazzl", "w") as f:
        yaml.dump(DEFAULT_SWARM, stream=f)


@cli.command()
@click.option("-g", "--gateway", "gateway", default=False, show_default=True, is_flag=True)
@click.argument("modules", nargs=-1, type=str, required=True)
def start(modules, gateway):
    swarm_definition = make_swarm_definition(gateway, modules)
    swarm = FrazzlSwarm()
    swarm.load_swarm(swarm_definition)
    swarm.start_swarm()


@cli.command()
@click.pass_context
def ls(ctx):
    print(FrazzlSwarm.validate(ctx.obj["swarm_definition"]))


if __name__ == '__main__':
    cli.main(prog_name="frazzl")
