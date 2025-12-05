#!/usr/bin/env python3
# setup.py

from setuptools import setup, find_packages

setup(
    name="container-security-utilities",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'docker',
        'pyyaml',
        'requests', 'fastapi'
    ],
    python_requires='>=3.8',
)
