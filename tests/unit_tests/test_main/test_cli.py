"""Tests."""
from typing import List

import pytest
from _pytest.capture import CaptureFixture

from boilerplatepython.__main__ import cli


def test_minimal():
    """Test with no optional arguments."""
    config = vars(cli(args=[]))

    assert config.pop("prog") in ("boilerplatepython", "pytest", "py.test", "_jb_pytest_runner.py")
    assert config.pop("color") is None
    assert config.pop("force_wide") is False
    assert config.pop("quiet") is False
    assert config.pop("verbose") == 0

    assert not config


def test_max():
    """Test with as many optional arguments as possible."""
    config = vars(
        cli(
            args=[
                "--color=never",
                "--force-wide",
                "-vvv",
            ]
        )
    )

    assert config.pop("prog") in ("boilerplatepython", "pytest", "py.test", "_jb_pytest_runner.py")
    assert config.pop("color") is False
    assert config.pop("force_wide") is True
    assert config.pop("quiet") is False
    assert config.pop("verbose") == 3

    assert not config


@pytest.mark.parametrize(
    "args",
    [
        ["--quiet", "--verbose"],
    ],
)
def test_mutually_exclusive(capsys: CaptureFixture, args: List[str]):
    """Test error handling of mutually exclusive options.

    :param capsys: pytest fixture.
    :param args: Arguments to test.
    """
    with pytest.raises(SystemExit):
        cli(args=args)

    stderr = capsys.readouterr()[1]
    assert " not allowed with argument " in stderr


def test_color_invalid(capsys: CaptureFixture):
    """Test invalid value.

    :param capsys: pytest fixture.
    """
    with pytest.raises(SystemExit):
        cli(args=["--color", "invalid"])

    stderr = capsys.readouterr()[1]
    assert " invalid choice:" in stderr
