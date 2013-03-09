#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1.7"


def read_long_description(filename="README.rst"):
    with open(filename) as f:
        return f.read().strip()


def read_requirements(filename="requirements.txt"):
    with open(filename) as f:
        return f.readlines()

if __name__ == '__main__':
    setup(
        name="cassette",
        version=__version__,
        author="Charles-Axel Dein",
        author_email="charles@uber.com",
        url="https://github.com/uber/cassette",
        packages=find_packages(),
        keywords=["http", "tests", "mock"],
        description="Cassette is a testing tool that stores external HTTP request in YAML file.",
        long_description=read_long_description(),
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
