from setuptools import setup, find_packages  # type: ignore
from bump_py_version import __version__

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]


setup(
    name="bump-py-version",
    version=__version__,
    description="Bump a python version in python files. Create a new tag and push it to git repository.",
    url="https://github.com/diversen/bump-py-version",
    author="Dennis Iversen",
    author_email="dennis.iversen@gmail.com",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "bump-py-version = bump_py_version.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.10",
    ],
)
