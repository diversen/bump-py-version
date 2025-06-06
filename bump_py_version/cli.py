import sys
import os
import tomlkit
import click
import subprocess


def parse_version_tag(tag):
    if tag.startswith("v"):
        return tag[1:]
    return tag


def alter_pyproject(version):
    version = parse_version_tag(version)

    with open("pyproject.toml", "r", encoding="utf-8") as f:
        content = f.read()
        pyproject = tomlkit.parse(content)

    if "project" in pyproject:
        pyproject["project"]["version"] = version

    if "tool" in pyproject:
        if "poetry" in pyproject["tool"]:
            pyproject["tool"]["poetry"]["version"] = version

    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(pyproject))


def alter_init(path, version):
    version = parse_version_tag(version)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("__version__ ="):
                f.write(f'__version__ = "{version}"\n')
            else:
                f.write(line)


def alter_text_file(file, str_search, replace):
    dynamic_next_line = False
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(file, "w", encoding="utf-8") as f:
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
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            pyproject = tomlkit.parse(f.read())
    except FileNotFoundError:
        pyproject = tomlkit.document()

    if os.path.exists("pyproject.toml"):
        alter_pyproject(version)

    try:
        version_file = pyproject["tool"]["bump_version"]["version_file"]
        alter_init(version_file, version)
    except KeyError:
        pass

    try:
        replace_patterns = pyproject["tool"]["bump_version"]["replace_patterns"]
        for _, pattern in replace_patterns.items():
            pattern["replace"] = pattern["replace"].replace("{version}", version)
            alter_text_file(pattern["file"], pattern["search"], pattern["replace"])
    except KeyError:
        pass


def run_command_check_untracked():
    status_message = (
        "There are untracked files. " "Use `git status` to see the files.\n" "Please remove or commit the files before running the command."
    )

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
    status_message = (
        "There are uncommited changes. " "Use `git status` to see the changes.\n" "Please commit the changes before running the command."
    )

    try:
        subprocess.run(
            "git diff-index --quiet HEAD --",
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError:
        print(status_message)
        sys.exit(1)


def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        error_message = "Command execution failed: " + str(e)
        print(error_message)
        sys.exit(1)


def bump_version(version):
    run_command_check_untracked()
    run_command_check_uncommited()
    alter_version(version)
    run_command("git add .")
    run_command(f'git commit -m "bump version to {version}"')
    run_command("git push")
    run_command(f'git tag -a {version} -m "bump version to {version}"')
    run_command("git push --tags")


def get_version():
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        pyproject = tomlkit.parse(f.read())
        return pyproject["project"]["version"]


PACKAGE_NAME = "MyPackage"

HELP = f"""bump-py-version v{get_version()}

Bump the version of a git-enabled python package

Usage:

    bump-py-version <version>

Example:

    bump-py-version v0.1.0
"""


@click.command(help=HELP)
@click.argument("version")
def cli(version):
    bump_version(version)


if __name__ == "__main__":
    cli()
