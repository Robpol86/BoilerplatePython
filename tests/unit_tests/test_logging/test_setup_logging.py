"""Tests."""
import logging
import warnings
from typing import Optional

import pytest
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from boilerplatepython.logging import LogFormatter, setup_logging
from .utils import __file__ as utils_filename, generate_log_statements


@pytest.fixture(autouse=True)
def _reset(request: FixtureRequest):
    """Reset global state after each test run.

    :param request: pytest fixture.
    """
    request.addfinalizer(warnings.resetwarnings)
    request.addfinalizer(lambda: logging.disable(logging.NOTSET))
    default_time_format_orig = LogFormatter.default_time_format
    request.addfinalizer(lambda: setattr(LogFormatter, "default_time_format", default_time_format_orig))


@pytest.mark.usefixtures("freeze_time")
def test_default(capsys: CaptureFixture, logger_name: str):
    """Test default values for arguments.

    :param capsys: pytest fixture.
    :param logger_name: conftest fixture.
    """
    log = setup_logging(logger_name=logger_name)
    assert not generate_log_statements(log)
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]

    expected_stdout = [
        "19T21:18:05.415 INFO: An info statement.",
    ]
    assert stdout == expected_stdout

    expected_stderr = [
        "19T21:18:05.415 WARN: This is a warning statement: 123",
        "19T21:18:05.415 ERRO: An error has occurred.",
        "19T21:18:05.415 CRIT: Critical failure: ERR",
        "19T21:18:05.415 ERRO: Here be an exception.",
    ]
    assert stderr == expected_stderr


def test_quiet(capsys: CaptureFixture, logger_name: str):
    """Test quiet.

    :param capsys: pytest fixture.
    :param logger_name: conftest fixture.
    """
    log = setup_logging(logger_name=logger_name, verbose=-1)
    assert not generate_log_statements(log)
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]
    assert not stdout
    assert not stderr


@pytest.mark.parametrize("verbose", [1, 2, 3])
@pytest.mark.usefixtures("freeze_time")
def test_verbose(capsys: CaptureFixture, logger_name: str, verbose: int):
    """Test verbose 1 - 3.

    :param capsys: pytest fixture.
    :param logger_name: conftest fixture.
    :param verbose: Verbosity level.
    """
    log = setup_logging(logger_name=logger_name, verbose=verbose)
    if verbose == 1:
        assert not generate_log_statements(log)
    else:
        assert generate_log_statements(log) == ["This thing shouldn't happen."]
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]

    expected_stdout = [
        "19T21:18:05.415 DBUG: Some debug statements: var",
        "19T21:18:05.415 INFO: An info statement.",
    ]
    assert stdout == expected_stdout

    expected_stderr = [
        "19T21:18:05.415 WARN: This is a warning statement: 123",
        "19T21:18:05.415 ERRO: An error has occurred.",
        "19T21:18:05.415 CRIT: Critical failure: ERR",
        "19T21:18:05.415 ERRO: Here be an exception.",
    ]
    if verbose == 3:
        expected_stderr += [
            "Traceback (most recent call last):",
            f'  File "{utils_filename}", line 21, in generate_log_statements',
            '    raise RuntimeError("An exception has occurred.")',
            "RuntimeError: An exception has occurred.",
        ]
    assert stderr == expected_stderr


@pytest.mark.usefixtures("freeze_time")
def test_colors(capsys: CaptureFixture, logger_name: str):
    """Test colors forced on.

    :param capsys: pytest fixture.
    :param logger_name: conftest fixture.
    """
    log = setup_logging(logger_name=logger_name, verbose=3, colors=True)
    generate_log_statements(log)
    output = [line for s in capsys.readouterr() for line in s.splitlines()]

    expected = [
        "19T21:18:05.415 \033[95mDBUG\033[0m: Some debug statements: var",
        "19T21:18:05.415 \033[36mINFO\033[0m: An info statement.",
        "19T21:18:05.415 \033[33mWARN\033[0m: This is a warning statement: 123",
        "19T21:18:05.415 \033[91mERRO\033[0m: An error has occurred.",
        "19T21:18:05.415 \033[91mCRIT\033[0m: Critical failure: ERR",
        "19T21:18:05.415 \033[91mERRO\033[0m: Here be an exception.",
        "Traceback \033[1;36m(most recent call last)\033[0m:",
    ]
    assert output[:len(expected)] == expected


@pytest.mark.parametrize("mock_tty", [False, True])
@pytest.mark.parametrize("colors", [None, False, True])
def test_auto_colors(
        capsys: CaptureFixture,
        monkeypatch: MonkeyPatch,
        logger_name: str,
        colors: Optional[bool],
        mock_tty: bool,
):
    """Test automatic colors based on TTY detection.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param logger_name: conftest fixture.
    :param colors: None == automatic, False == force off, True == force on.
    :param mock_tty: Mock a tty on stdout.
    """
    if mock_tty:
        monkeypatch.setattr("boilerplatepython.logging.STDOUT_ISATTY", True)

    log = setup_logging(logger_name=logger_name, colors=colors)
    generate_log_statements(log)
    output = capsys.readouterr()[1].splitlines()[0]

    if colors is True:
        assert "\033" in output
    elif colors is False:
        assert "\033" not in output
    else:
        if mock_tty:
            assert "\033" in output
        else:
            assert "\033" not in output
