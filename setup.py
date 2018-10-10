from setuptools import setup, find_packages
from os import path

required = ["pipenv"]

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pipenv-cli-patch",
    version="0.0.1",
    author="Guilherme Zagatti",
    author_email="gzagatti@gmail.com",
    description=("Convenience patches for the pipenv CLI."),
    license="MIT",
    keywords="pipenv cli",
    packages=["src"],
    entry_points={
        "console_scripts": [
            "pipenv=src:patched_cli",
            ]
    },
    long_description=long_description,
)

