#!/usr/bin/env python
from setuptools import setup

__VERSION__ = "0.1"


def read_requirements(filename="requirements.txt"):
    with open(filename) as f:
        return f.readlines()

setup(
    name="cassette",
    version=__VERSION__,
    author="Charles-Axel Dein",
    author_email="charles@uber.com",
    packages=["cassette"],
    description="Cassette is a testing tool that stores external HTTP request in YAML file.",
    install_requires=read_requirements(),
)
