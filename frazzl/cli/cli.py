import logging

import click

from frazzl.core.constants import VERSION


@click.group()
@click.version_option(version=VERSION)
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    frazzl_logger = logging.getLogger("frazzl-cli")
    if verbose:
        frazzl_logger.setLevel(logging.INFO)
        logging.getLogger("frazzl").setLevel(logging.INFO)
    ctx.obj = {"logger": frazzl_logger}
