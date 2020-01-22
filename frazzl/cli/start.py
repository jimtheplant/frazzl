import click

from frazzl.cli.cli import cli
from frazzl.core.exceptions import ConfigError
from frazzl.core.types.swarm.gateway import GatewayNode
from frazzl.core.types.swarm.node import AppNode


@cli.command(
    help="Start a singular frazzl app.",
    short_help="start a singular frazzl app",
    add_help_option=True,
)
@click.argument("app")
@click.option(
    "--port",
    "-p",
    type=click.INT,
    default=8000,
    show_default=True,
    help="The port to access the node."
)
@click.option(
    "--gateway",
    "-g",
    is_flag=True,
    help="Start a gateway pointing to the started app."
)
@click.pass_context
def start(ctx, app, port, gateway):
    logger = ctx.obj["logger"]
    if len(app.split(":")) != 2:
        logger.error("App argument must be in format namespace:appName.")
        exit(1)
    namespace, app_name = tuple(app.split(":"))
    definition = {"namespace": namespace, "settings": {"port": port}, "name": app_name}
    try:
        node = AppNode.build(definition)
        node.start()
        if gateway:
            gateway = GatewayNode.build({"local": "true", "nodes": [app_name]}, nodes={app_name: node})
            gateway.start()
    except ConfigError as e:
        logger.error(str(e))
        exit(1)
