import os
import subprocess

import click

from frazzl.core.constants import VERSION
from frazzl.core.types.swarm.swarm import FrazzlSwarm
from frazzl.core.util.swarm import make_swarm_definition


@click.group()
@click.version_option(version=VERSION)
def cli():
    pass


@cli.command()
def init():
    gateway_path = os.path.join(os.path.dirname(__file__), "gateway")
    subprocess.run("nodeenv -p".split())
    subprocess.run("npm install", cwd=gateway_path, shell=True)


@cli.command()
@click.option("-g", "--gateway", "gateway", default=False, show_default=True, is_flag=True)
@click.argument("modules", nargs=-1, type=str, required=True)
def start(modules, gateway):
    swarm_definition = make_swarm_definition(gateway, modules)
    swarm = FrazzlSwarm()
    swarm.load_swarm(swarm_definition)
    swarm.start_swarm()


@cli.command()
@click.option("-g", "--gateway", "gateway", default=False, show_default=True, is_flag=True)
@click.argument("modules", nargs=-1, type=str, required=True)
def list(modules, gateway):
    swarm_definition = make_swarm_definition(gateway, modules)
    swarm = FrazzlSwarm()
    swarm.validate(swarm_definition)


if __name__ == '__main__':
    cli.main(prog_name="frazzl")
