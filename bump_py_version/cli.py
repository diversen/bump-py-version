"""
This script is used to bump the version of the package.

It will exit if there are uncommited changes to prevent
accidental commits.

Usage:

    bump-py-version <version>

"""

import sys
import os
import toml
import click
import subprocess


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
        version_file = pyproject["tool"]["bump_version"]["version_file"]
        alter_init(version_file, version)
    except KeyError:
        pass

    # Alter text files
    try:
        replace_patterns = pyproject["tool"]["bump_version"]["replace_patterns"]
        for _, pattern in replace_patterns.items():
            pattern["replace"] = pattern["replace"].replace("{version}", version)
            alter_text_file(pattern["file"], pattern["search"], pattern["replace"])
    except KeyError:
        pass


def run_command_check_untracked():
    """
    function that checks if there are untracked files
    """

    status_message = "There are untracked files. "
    status_message += "Use `git status` to see the files.\n"
    status_message += "Please remove or commit the files before running the command. "

    result = subprocess.run(
        "git ls-files --others --exclude-standard",
        check=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.stdout.strip():
        print(status_message)
        sys.exit(1)


def run_command_check_uncommited():
    """
    function that checks if there are uncommited changes
    """

    status_message = "There are uncommited changes. "
    status_message += "Use `git status` to see the changes.\n"
    status_message += "Please commit the changes before running the command."

    try:
        subprocess.run(
            "git diff-index --quiet HEAD --",
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except Exception:
        print(status_message)
        sys.exit(1)


def run_command(command):

    try:
        # Run the command and capture the output
        subprocess.run(command, check=True, shell=True)

    except subprocess.CalledProcessError as e:
        # Append the exception message to the status message
        error_message = "Command execution failed: " + str(e)
        print(error_message)
        sys.exit(1)


def bump_version(version):

    # Check if there are files that are not tracked. If there are, exit
    run_command_check_untracked()

    # Check if there are uncommited changes
    run_command_check_uncommited()

    # Alter the version in the files
    alter_version(version)

    # Add the changes
    run_command("git add .")

    # Commit the changes
    run_command(f'git commit -m "bump version to {version}"')

    # Push the changes
    run_command("git push")

    # Create a tag
    run_command(f'git tag -a {version} -m "bump version to {version}"')

    # Push the tag
    run_command("git push --tags")


def get_version():
    """Reads version from pyproject.toml at runtime, only when needed."""
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
        return pyproject["project"]["version"]


PACKAGE_NAME = "MyPackage"  # Your dynamic variable

HELP = f"""Bump the version of a git-enabled python package

Usage:

bump-py-version <version>

Version:

{get_version()}
"""

@click.command(help=HELP)

@click.argument("version")
def cli(version):

    bump_version(version)


if __name__ == "__main__":
    cli()
