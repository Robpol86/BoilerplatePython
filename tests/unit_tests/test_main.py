"""Tests."""
import signal
from typing import List

import pytest
from _pytest.capture import CaptureFixture

from boilerplatepython.__main__ import cli, ExitSignaling


def test_cli_minimal():
    """Test with no optional arguments."""
    config = cli(args=[])

    assert config.prog in ("boilerplatepython", "pytest", "py.test")
    assert config.bell is None
    assert config.color is None
    assert config.extended == 0
    assert config.quiet is False
    assert config.verbose == 0


@pytest.mark.parametrize("args", [
    ["--quiet", "--verbose"],
])
def test_cli_mutually_exclusive(capsys: CaptureFixture, args: List[str]):
    """Test error handling of mutually exclusive options.

    :param capsys: pytest fixture.
    :param args: Arguments to test.
    """
    with pytest.raises(SystemExit):
        cli(args=args)

    stderr = capsys.readouterr()[1]
    assert " not allowed with argument " in stderr


@pytest.mark.parametrize("extended", [1, 2, 3, 4])
def test_cli_extended(extended: int):
    """Test option."""
    config = cli(args=(["--extended-output"] * extended))
    assert config.extended == extended


@pytest.mark.parametrize("verbose", [1, 2, 3, 4])
def test_cli_verbose(verbose: int):
    """Test option."""
    config = cli(args=(["--verbose"] * verbose))
    assert config.verbose == verbose


@pytest.mark.parametrize("bell", ["never", "always", "auto"])
def test_cli_bell(bell: str):
    """Test option."""
    config = cli(args=["--bell", bell])
    if bell == "never":
        assert config.bell is False
    elif bell == "always":
        assert config.bell is True
    else:
        assert config.bell is None


@pytest.mark.parametrize("color", ["never", "always", "auto"])
def test_cli_color(color: str):
    """Test option."""
    config = cli(args=["--color", color])
    if color == "never":
        assert config.color is False
    elif color == "always":
        assert config.color is True
    else:
        assert config.color is None


def test_cli_color_invalid(capsys: CaptureFixture):
    """Test invalid value.

    :param capsys: pytest fixture.
    """
    with pytest.raises(SystemExit):
        cli(args=["--color", "invalid"])

    stderr = capsys.readouterr()[1]
    assert " invalid choice:" in stderr


def test_exit_signaling():
    """Test."""
    exit_signaling = ExitSignaling()
    assert exit_signaling.exit_code == 0

    with pytest.raises(SystemExit) as exc:
        exit_signaling.exit(signal.SIGTERM, None)

    assert exc.value.code == 143
