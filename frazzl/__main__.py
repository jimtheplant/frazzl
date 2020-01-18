import logging
import os
import subprocess

import click
import yaml

from frazzl.core.constants import VERSION, DEFAULT_SWARM
from frazzl.core.exceptions import ConfigError
from frazzl.core.types.swarm.swarm import FrazzlSwarm
from frazzl.core.util.swarm import update_swarm_definition

frazzl_logger = logging.getLogger("frazzl")


@click.group()
@click.version_option(version=VERSION)
@click.option("--swarm-config", "-c", type=click.Path(), default="frazzl-swarm.yaml")
@click.option("--verbose", "-v", type=click.BOOL, default=False)
@click.pass_context
def cli(ctx, swarm_config, verbose):
    if verbose:
        frazzl_logger.setLevel(logging.INFO)
    if ctx.invoked_subcommand is not "init":
        combined_definition = {}
        try:
            project_definition = FrazzlSwarm.swarm_definition_from_yaml(".frazzl")
            combined_definition = update_swarm_definition(
                project_definition,
                FrazzlSwarm.swarm_definition_from_yaml(swarm_config)
            )
        except ConfigError as e:
            frazzl_logger.warning(f"{str(e)}")
            pass
        ctx.obj = {"swarm_definition": combined_definition}


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
@click.pass_context
def start(ctx):
    with FrazzlSwarm.start_swarm(ctx.obj["swarm_definition"]) as swarm:
        pass


@cli.command()
@click.pass_context
def ls(ctx):
    context = FrazzlSwarm.validate(ctx.obj["swarm_definition"])
    logging.getLogger("frazzl").info("testing")


if __name__ == '__main__':
    cli.main(prog_name="frazzl")
