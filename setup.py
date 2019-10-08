from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os


class PostInstallCommand(install):
    def run(self):
        if os.name == "nt":
            activate_script = "activate.bat"
        else:
            activate_script = "activate"
        gateway_path = os.path.join(os.getcwd(), "gateway")
        activatecmd = os.path.join(gateway_path, "node", "Scripts", activate_script)
        subprocess.run("nodeenv node".split(), cwd=gateway_path)
        subprocess.run([activatecmd] + " & npm install".split(), cwd=gateway_path)
        install.run(self)


setup(
    name="graphqlflow",
    version="0.0.1",
    author="jimtheplant",
    author_email="jimtheplant1@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    cmdclass={
        "install": PostInstallCommand
    },
    install_requires=[
        "ariadne>=0.7",
        "uvicorn",
        "nodeenv"
    ]
)