from setuptools import setup, find_packages

setup(
    name="graphqlflow",
    version="0.0.1",
    author="jimtheplant",
    author_email="jimtheplant1@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "ariadne>=0.7",
        "uvicorn",
        "nodeenv"
    ]
)