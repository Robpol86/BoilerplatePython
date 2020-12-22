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

For Debian running from WSL 2:

```bash
sudo apt-get update && apt-get install python3-pip python3-venv
python3.7 -m pip install -U pip poetry setuptools wheel
export PATH="$PATH:$HOME/.local/bin"
POETRY_VIRTUALENVS_IN_PROJECT=true poetry env use "$(which python3.7)"
```

Then see if you can run lints and tests:

```bash
make lint
make test
make it
```
