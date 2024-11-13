# Copyright (C) 2024 twyleg
import versioneer
from setuptools import find_packages, setup
from pathlib import Path


def read(fname):
    return open(Path(__file__).parent / fname).read()


# fmt: off
setup(
    name="track_generator",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description="Track generator",
    license="GPL 3.0",
    keywords="svg model vehicles track",
    url="https://github.com/twyleg/track_generator",
    packages=find_packages(),
    include_package_data=True,
    long_description=read("README.md"),
    install_requires=[
        "pytransform3d~=3.2.0",
        "drawsvg==1.9",
        "watchdog~=3.0.0",
        "simple-python-app-qt==0.0.4"
    ],
    entry_points={
        "console_scripts": [
            "track_generator = track_generator.starter:main",
        ]
    },
)
