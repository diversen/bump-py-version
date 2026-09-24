# bump-py-version

This is a simple and opinionated python `tool` to bump the of a python package.

1. The script will check for any changes in the current `git` repository and abort if there are any.

2. If there are no changes, it will check for a `version` field in `pyproject.toml`. If the `project.version` exist it is altered to the specified version. Other options are specified below. 

3. The script commits and pushes the changes. 
4. Then a new tag is created using the new `version` specified to the script.
5. Finally the script pushes the new tag to the remote repository.

## Installation

Install latest version:

<!-- LATEST-VERSION-UV -->
	uv tool install git+https://github.com/diversen/bump-py-version@v2.0.6

## Configuration

You may also bump the python version `__version__` in e.g.  `__init__.py` file (or similar) using a `pyproject.toml` setting like the following:

```toml
[tool.bump_version]
version_file = "bump_py_version/__init__.py"
```

You may configure the script to alter text files (e.g. `README.md`) by setting the section `tool.bump_version.replace_patterns` in the `pyproject.toml` file. Example:

```toml
[tool.bump_version.replace_patterns.pipx]
file = "README.md"
search = "<!-- LATEST-VERSION-UV -->"
replace = "\tuv tool install git+https://github.com/diversen/bump-py-version@{version}\n"

```

The above will cause the line below the `search` string to be replaced with the `replace` string. Then it is easy to show the latest version of the package in a `README.md` file.

### Updating uv.lock

To update `uv.lock` as part of each version bump, enable:

```toml
[tool.bump_version]
uv_lock = true
```

This runs `uv lock` after updating the version files and before staging changes,
so the lockfile is included in the release commit and tag. It does not request
dependency upgrades. If the lockfile does not exist, `uv lock` creates it.

`uv` must be installed and available on `PATH`. The command checks these
prerequisites before modifying files and rejects an ignored `uv.lock`, explaining
that it must be removed from `.gitignore` or the applicable Git ignore rules.
An existing, untracked lockfile must be committed before bumping, just like any
other non-ignored untracked file.

If `uv lock` fails, the command stops before committing, pushing, or tagging;
local edits remain available for inspection. The setting defaults to `false`,
which preserves the existing behavior without running `uv`.

## Usage example

Example:

```bash
bump-py-version v1.2.3
```

# License

MIT © [Dennis Iversen](https://github.com/diversen)
