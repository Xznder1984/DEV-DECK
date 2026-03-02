#!/usr/bin/env python3
"""
Setup script for DevDeck.
This script allows installing DevDeck as a Python package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="devdeck",
    version="1.0.0",
    author="Xznder",
    author_email="xznder@example.com",
    description="A powerful local developer control panel for programmers and IT enthusiasts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xznder1984/DEV-DECK",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "devdeck=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
