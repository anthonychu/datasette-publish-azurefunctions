from setuptools import setup
import os

VERSION = "1.0.0"


def get_long_description():
    "Azure Functions Datasette publish plugin"


setup(
    name="datasette-publish-azurefunctions",
    description="Datasette plugin for publishing data using Azure Functions",
    long_description=get_long_description(),
    long_description_content_type="text/plain",
    author="Anthony Chu",
    url="https://github.com/anthonychu",
    project_urls={
        "Issues": "https://github.com/anthonychu",
        "CI": "https://github.com/anthonychu",
    },
    license="MIT",
    version=VERSION,
    packages=["datasette_publish_azurefunctions"],
    entry_points={"datasette": ["publish_azurefunctions = datasette_publish_azurefunctions"]},
    install_requires=["datasette>=0.54", "termcolor"],
)