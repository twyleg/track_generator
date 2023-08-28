# Copyright (C) 2022 twyleg
from pathlib import Path

import versioneer
from setuptools import find_packages, setup


def read(fname):
    return open(Path(__file__).parent / fname).read()


setup(
    name="track_generator",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description=("Track generator"),
    license="GPL 3.0",
    keywords="svg model vehicles track",
    url="https://github.com/twyleg/track_generator",
    packages=find_packages(),
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    install_requires=[
        "pytransform3d~=3.2.0",
        "drawsvg[all]~=2.2.0",
        "watchdog~=3.0.0",
        "pyside6>=6.2.4",
        "xmlschema~=2.3.1",
        "jinja2~=3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "track_generator = track_generator.starter:start",
        ]
    },
)
