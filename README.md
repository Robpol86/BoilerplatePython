# BoilerplatePython

Boilerplate for my Python projects. Using Poetry instead of setuptools.

## Local Development

This project runs on Python 3.7 or greater, and relies on [Python Poetry](https://python-poetry.org).

To develop on macOS use [Homebrew](https://brew.sh):

```bash
brew install python@3.7
brew install poetry
make clean
POETRY_VIRTUALENVS_IN_PROJECT=true poetry env use "$(brew --prefix)/opt/python@3.7/bin/python3"
```

Then see if you can run lints and tests:

```bash
make lint
make test
make it
```
