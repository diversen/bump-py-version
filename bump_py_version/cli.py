"""
This script is used to bump the version of the package.
It will change the version in the pyproject.toml file,
the __init__.py file and the README.md file.

It will exit if there are uncommited changes to prevent
accidental commits.

Usage:

    bump-py-version <version>

"""

import sys
import os
import toml
import re
import logging
import click


logging.basicConfig(level=logging.DEBUG)


def parse_version_tag(tag):
    """
    Remove leading 'v' if it exists
    """
    if tag.startswith("v"):
        return tag[1:]

    return tag


def alter_pyproject(pyproject, version):
    """
    function that
    changes the project version and the poetry version
    in the pyproject.toml file
    """

    version = parse_version_tag(version)

    if "project" in pyproject:
        pyproject["project"]["version"] = version

    if "tool" in pyproject:
        if "poetry" in pyproject["tool"]:
            pyproject["tool"]["poetry"]["version"] = version

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)


def alter_init(path, version):
    """
    function that changes the version in the __init__.py file
    """
    version = parse_version_tag(version)
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        for line in lines:
            if line.startswith("__version__ ="):
                f.write(f'__version__ = "{version}"\n')
            else:
                f.write(line)


def alter_text_file(file, str_search, replace):
    """
    function that changes the version in a text file
    it searches for a string and replaces the line below
    with the replace string
    """
    dynamic_next_line = False
    with open(file, "r") as f:
        lines = f.readlines()
    with open(file, "w") as f:
        for line in lines:
            if dynamic_next_line:
                f.write(replace)
                dynamic_next_line = False
            elif line.startswith(str_search):
                f.write(line)
                dynamic_next_line = True
            else:
                f.write(line)


def alter_version(version):
    pyproject = {}

    try:
        with open("pyproject.toml", "r") as f:
            pyproject = toml.load(f)

    except FileNotFoundError:
        pass

    # Alter pyproject.toml
    if os.path.exists("pyproject.toml"):
        alter_pyproject(pyproject, version)

    # Alter __init__.py
    try:
        version_file = pyproject["tool"]["bumptag"]["version_file"]
        alter_init(version_file, version)
    except KeyError:
        pass

    # Alter text files
    try:
        replace_patterns = pyproject["tool"]["bumptag"]["replace_patterns"]
        for _, pattern in replace_patterns.items():
            pattern["replace"] = pattern["replace"].replace("{version}", version)
            alter_text_file(pattern["file"], pattern["search"], pattern["replace"])
    except KeyError:
        pass


def bump_version(version):
    # check if something needs to be commited
    # if something needs to be commited, exit
    if os.system("git diff-index --quiet HEAD --") != 0:
        print("There are uncommited changes")
        sys.exit(1)

    # change the version in the files
    alter_version(version)

    # commit the changed files
    os.system("git add .")
    os.system(f'git commit -m "bump version to {version}"')
    os.system("git push")

    # create tag
    os.system(f'git tag -a {version} -m "bump version to {version}"')
    os.system("git push --tags")


@click.command()
@click.argument("version")
def cli(version):
    """
    Bump the version of the package
    """
    bump_version(version)


if __name__ == "__main__":
    cli()
