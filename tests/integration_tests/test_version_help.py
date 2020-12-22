"""Tests."""
import subprocess
import sys
from pathlib import Path


def test_version():
    """Verify multi-sourced versions are synchronized."""
    # Get version from Poetry.
    output = subprocess.check_output(["poetry", "version", "--no-interaction"]).strip()
    version_poetry = output.split()[1].decode("utf8")

    # Get version from program.
    output = subprocess.check_output(["poetry", "run", "boilerplatepython", "-V"]).strip()
    version_program = output.decode("utf8")

    assert version_poetry == version_program


def test_changelog():
    """Verify current version is included in the changelog file."""
    version = subprocess.check_output([sys.executable, "-m", "boilerplatepython", "-V"]).strip().decode("utf8")
    changelog = Path(__file__).parent.parent.parent / "CHANGELOG.md"

    with changelog.open("r") as handle:
        changelog_head = handle.read(1024).splitlines()

    assert [line for line in changelog_head if line.startswith(f"## [{version}] - ")]


def test_help():
    """Verify --help."""
    command = ["boilerplatepython", "--help"]

    output = subprocess.check_output(command)
    assert b"show this help message and exit" in output
