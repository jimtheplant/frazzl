from setuptools import setup, find_packages
from frazzl.constants import VERSION

setup(
    name="frazzl",
    version=VERSION,
    author="jimtheplant",
    author_email="jimtheplant1@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "frazzl=frazzl.__main__:cli"
        ]
    },
    install_requires=[
        "ariadne==0.7",
        "uvicorn==0.11.7",
        "nodeenv==1.3.3",
        "click==7.0"
    ]
)
