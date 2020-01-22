import click

from frazzl.cli import cli
from frazzl.core.exceptions import ConfigError
from frazzl.core.types.swarm.swarm import FrazzlSwarm
from frazzl.core.util.cli import update_default_frazzl_file


@cli.group(
    help="Commands that configure and list the global settings of a frazzl project.",
    short_help="configure and list global settings",
    add_help_option=True,
)
@click.option(
    "--file",
    "-f",
    type=click.Path(),
    default=".frazzl",
    show_default=True,
    help="The frazzl project file that defines global settings."
)
@click.pass_context
def settings(ctx, file):
    try:
        ctx.obj["project_file"] = file
        ctx.obj["global_definition"] = FrazzlSwarm.swarm_definition_from_yaml(file)
    except ConfigError as e:
        ctx.obj["logger"].error(str(e))
        exit(1)


@settings.command(
    help="Lists the global settings of the project for the current environment.",
    short_help="list global settings",
    add_help_option=True,
)
@click.pass_context
def ls(ctx):
    global_definition = ctx.obj["global_definition"]
    global_settings = global_definition["settings"]
    environment = global_settings['environment']

    click.echo(
        f"Start gateway by default? {'true' if global_definition['gateway']['local'] in ['true', 'True'] else 'false'}"
    )

    click.echo(f"Current enviornment: {environment}")
    click.echo(f"{environment} settings:")
    environment_settings = global_settings.get(environment, None)
    if not environment_settings:
        ctx.obj["logger"].error(f"No settings found for the current environment {environment}")
        exit(1)
    for setting, value in global_settings[environment].items():
        click.echo(f"\t{setting}: {value}")


@settings.command(
    help="Opens an editor to change the global settings of the project.",
    short_help="edit the global settings",
    add_help_option=True,
)
@click.option("--reset", is_flag=True, help="reset the settings back to default before editing")
@click.pass_context
def edit(ctx, reset):
    if reset:
        update_default_frazzl_file()
        project_file = ".frazzl"
    else:
        project_file = ctx.obj["project_file"]
    click.edit(filename=project_file)
    ctx.obj["logger"].info("Project settings changed.")
