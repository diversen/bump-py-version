# bump-py-version

This is a simple and opinionated script to bump the version of a python package.

1. The script will check for any changes in the git repository and abort if there are any.
2. If there are no changes, it will alter files where a `version` is set, e.g. `pyproject.toml` or `__init__.py`. (Which files to alter are specified in the `pyproject.toml` file according to the `tool.bump_version` section.)
3. The script commits and pushes the changes. 
4. Then a new tag is created using the `version` tag specified.
5. Finally the script pushes the tag to the remote repository.

## Installation

<!-- LATEST-VERSION-PIPX -->
	pipx install git+https://github.com/diversen/bump-py-version@v1.2.0

## Configuration

It may bump the version in a `__init__.py` file (or similar) using a pyproject settings like the following:

```toml
[tool.bump_version]
version_file = "bump_py_version/__init__.py"
```

**Note** about `setup.py`. `setup.py` should import the version from the `__init__.py` file. Example:

```python
from bump_py_version import __version__
```

If you have a pyproject file with a `project.version` or a `tool.poetry.version` section then the script will bump these versions too. 

You may configure the script to alter text files (e.g. `README.md`) by setting the section `tool.bump_version.replace_patterns` in the `pyproject.toml` file. Example:

```toml
[tool.bump_version.replace_patterns.pip]
file = "README.md"
search = "<!-- LATEST-VERSION-PIP -->"
replace = "\tpip install git+https://github.com/diversen/bump-py-version@{version}\n"

[tool.bump_version.replace_patterns.pipx]
file = "README.md"
search = "<!-- LATEST-VERSION-PIPX -->"
replace = "\tpipx install git+https://github.com/diversen/bump-py-version@{version}\n"
```

The above will cause the line below the `search` string to be replaced with the `replace` string. Then it is easy to show the latest version of the package in a `README.md` file.

## Usage example

Example:

```bash
bump-py-version v0.0.1
```
