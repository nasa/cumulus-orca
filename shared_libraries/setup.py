#!/usr/bin/env python3
from io import open
import os
import re
from setuptools import setup, find_packages
import sys
import orca_shared.__init__ as library_list

# Borrowed from pip at https://github.com/pypa/pip/blob/62c27dee45625e1b63d1e023b0656310f276e050/setup.py#L11-L15
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def get_version():
    version_file = read("orca_shared", "__init__.py")
    version_match = re.search(
        r'^__version__ = [\'"]([^\'"]*)[\'"]', version_file, re.MULTILINE
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# General installation requirements
install_requirements = ["aws_lambda_powertools==1.31.0"]


# Additional library dependencies
_dep_boto3 = "boto3~=1.18.40"
_dep_sqlalchemy = "SQLAlchemy~=2.0.5"


# Get all the libraries available in the orca_shared space
extras_per_library = {}
for library_name in [
    library[7:] for library in dir(library_list) if library.startswith("shared_")
]:
    extras_per_library[library_name] = []


# Update with library specific requirements
extras_per_library.update(
    {"database": [_dep_boto3, _dep_sqlalchemy], "recovery": [_dep_boto3], "reconciliation": []}
)


# Get all the extra dependencies from the extras_per_library dictionary
all_extras = []
for library_name in extras_per_library:
    new_dependencies = set(extras_per_library[library_name]) - set(all_extras)
    all_extras = all_extras + list(new_dependencies)


# Provide the extra requirements for when everything is installed
extras_per_library["all"] = all_extras


# Perform the setup
setup(
    name="orca_shared",
    version=get_version(),
    description="ORCA libraries used as helpers for several tasks.",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=install_requirements,
    extras_require=extras_per_library,
    include_package_data=True,
)
