# bump-py-version

This is a simple and opinionated script to bump the version of a python package.

## Installation

<!-- LATEST-VERSION-PIPX -->
	pipx install git+https://github.com/diversen/bump-py-version@v0.0.8

It may bump the version in a `__init__.py` file (or similar) using a pyproject settings like the following:

```toml
[tool.bumptag]
version_file = "bump_py_version/__init__.py"
```

`setup.py` should import the version from the package (if you use a `setup.py` file). In order to
only have one python variable with the version number. Something like this:

```python
from setuptools import setup
from bump_py_version import __version__
```

If you have a pyproject file with a `project.version` or a `tool.poetry.version` then the script will bump these versions too. 

You may configure the script to alter text files (e.g. `README.md`). 

```toml
[tool.bumptag.replace_patterns.pip]
file = "README.md"
search = "<!-- LATEST-VERSION-PIP -->"
replace = "\tpip install git+https://github.com/diversen/bump-py-version@{version}\n"
```

The above will cause the line below the `search` string to be replaced with the `replace` string.
Then it is easy to show the latest version of the package in a README.md file.

## Usage

Example:

```bash
bump-py-version v0.0.1
```

1. The script will check for any changes in the git repository and abort if there are any.
2. If there is no changes, it will alter the version as specified in the `pyproject.toml` file.
3. The script commits and pushes the changes. 
4. Then the script creates a new tag with the version number.
5. Finally the script pushes the tag to the remote repository.
