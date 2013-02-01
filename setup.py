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
    url="https://github.com/uber/cassette",
    packages=["cassette"],
    keywords=["http", "tests", "mock"],
    description="Cassette is a testing tool that stores external HTTP request in YAML file.",
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
