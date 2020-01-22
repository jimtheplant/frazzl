import click

from frazzl.cli import cli
from frazzl.core.exceptions import ConfigError
from frazzl.core.types.swarm.swarm import FrazzlSwarm
from frazzl.core.util.swarm import update_swarm_definition


@cli.group(
    help="Commands to start multiple frazzl nodes.",
    short_help="start multiple frazzl nodes",
    add_help_option=True
)
@click.option(
    "--file",
    "-f",
    type=click.Path(),
    default="frazzl-swarm.yaml",
    show_default=True,
    help="The frazzl swarm file that defines the settings for the swarm."
)
@click.pass_context
def swarm(ctx, file):
    swarm_definition = {}
    try:
        swarm_definition = update_swarm_definition(
            FrazzlSwarm.swarm_definition_from_yaml(".frazzl"),
            FrazzlSwarm.swarm_definition_from_yaml(file))
    except ConfigError as e:
        ctx.obj["logger"].warn(str(e))
        pass

    ctx.obj["swarm_definition"] = swarm_definition


@swarm.command(
    help="Validates that the swarm definition can be built and started.",
    short_help="validate the swarm definition",
    add_help_option=True
)
@click.pass_context
def validate(ctx):
    try:
        FrazzlSwarm.validate(ctx.obj["swarm_definition"])
    except ConfigError as e:
        ctx.obj["logger"].error(str(e))
        click.echo("Swarm definition is not valid. See error above for help.")
        exit(1)
    click.echo("Swarm definition is valid.")


@swarm.command(
    help="Starts the swarm with options for a gateway node, "
         "and specifying individual nodes. If --all flag is not set, nodes are required as arguments.",
    short_help="start multiple frazzl nodes",
    add_help_option=True
)
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help="Start all nodes in the swarm definition. Ignores node arguments."
)
@click.option(
    "--gateway",
    "-g",
    type=click.BOOL,
    default=None,
    help="Toggles the gateway option to start the gateway."
)
@click.argument(
    "nodes",
    nargs=-1,
    required=False
)
@click.pass_context
def start(ctx, all, gateway, nodes):
    swarm_definition = ctx.obj["swarm_definition"]
    nodes = list(nodes)
    with FrazzlSwarm.start_swarm(swarm_definition, rebuild=True) as swarm:
        if gateway is not None:
            swarm.gateway = swarm.gateway if gateway else None
        if not all:
            if len(nodes) == 0:
                ctx.obj["logger"].error("No nodes were given and the --all flag was not set.")
                exit(1)
            nodes_to_remove = []
            for node_name in swarm.nodes.keys():
                if node_name not in nodes:
                    nodes_to_remove.append(node_name)
                nodes.remove(node_name)
            for leftover_node in nodes:
                ctx.obj["logger"].warn(f"{leftover_node} was not found in the swarm definition. "
                                       f"{leftover_node} was not started.")
            for node_name in nodes_to_remove:
                del swarm.nodes[node_name]
            if len(swarm.nodes.keys()) == 0:
                ctx.obj["logger"].error(f"The given nodes {[n for n in nodes]} were not found "
                                        f"in the swarm definition an no other valid nodes were found.")
                exit(1)
