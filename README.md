# bump-py-version

This is a simple and opinionated script to bump the version of a python package.

## Installation

<!-- LATEST-VERSION-PIPX -->
    pipx install git+https://github.com/diversen/bump-py-version@v0.0.1

It will bump the version in the `__init__.py` (or similar) using 
a pyproject settings like the following:

```toml
[tool.bumptag]
version_file = "bump_py_version/__init__.py"
```

`setup.py` should import the version from the package (if using `setup.py`).

```python
from setuptools import setup
from bump_py_version import __version__
```

You may also configure the script to alter text files (e.g. `README.md`). 

```toml
[tool.bumptag.replace_patterns.pip]
file = "README.md"
search = "<!-- LATEST-VERSION-PIP -->"
replace = "\tpip install git+https://github.com/diversen/bump-py-version@{version}\n"
```

The above will cause the line below the `search` string to be replaced with the `replace` string.
Then it is easy to show the latest version of the package in the README.md file.

## Usage

The script will check for any changes in the git repository and abort if there are any.
If there is no changes, it will alter the version as specified in the `pyproject.toml` file.
It will commit and push the changes. Then it will tag the commit with the new version.
Finally it will push the commit and the tag to the remote repository.

```bash
bump-my-version v0.0.1
```
