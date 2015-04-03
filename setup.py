#!/usr/bin/env python
from setuptools import setup, find_packages


def read_long_description(filename="README.rst"):
    with open(filename) as f:
        return f.read().strip()


def read_requirements(filename="requirements.txt"):
    with open(filename) as f:
        return f.readlines()

setup(
    name="cassette",
    version='0.3.8',
    author="Charles-Axel Dein",
    author_email="charles@uber.com",
    url="http://cassette.readthedocs.org/",
    license="MIT",
    packages=find_packages(),
    keywords=["http", "tests", "mock"],
    description="Cassette stores and replays HTTP requests.",
    long_description=read_long_description(),
    install_requires=read_requirements(),
    tests_require=[
        'pytest',
        'mock',
        'flask',
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
