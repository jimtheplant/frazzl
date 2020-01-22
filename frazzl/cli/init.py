import os
import subprocess

from frazzl.cli import cli
from frazzl.core.util.cli import update_default_frazzl_file


@cli.command(
    help="Initializes a frazzl project. Installs required javascript dependencies and creates a default settings file.",
    short_help="initialize a frazzl project",
    add_help_option=True,
)
def init():
    gateway_path = os.path.join(os.path.dirname(__file__), "../gateway")
    subprocess.run("nodeenv -p".split())
    subprocess.run("npm install", cwd=gateway_path, shell=True)
    update_default_frazzl_file()
