import os
import subprocess
import click
from .constants import VERSION


@click.group()
@click.version_option(version=VERSION)
def cli():
    pass


@cli.command()
def init():
    gateway_path = os.path.join(os.path.dirname(__file__), "gateway")
    subprocess.run("nodeenv -p".split())
    subprocess.run("npm install", cwd=gateway_path, shell=True)


if __name__ == '__main__':
    cli.main(prog_name="frazzl")
