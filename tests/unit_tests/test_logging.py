"""Tests."""
import logging
import os
import sys
import time
import warnings
from typing import Optional

import pytest
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from boilerplatepython.logging import LogFormatter, setup_logging
from .utils import __file__ as utils_filename, generate_log_statements


@pytest.fixture(autouse=True, scope="session")
def _setup():
    """Run for all tests."""
    os.environ["TZ"] = "UTC"
    time.tzset()


@pytest.fixture(autouse=True)
def _reset(request: FixtureRequest):
    """Reset global state after each test run.

    :param request: pytest fixture.
    """
    request.addfinalizer(warnings.resetwarnings)
    request.addfinalizer(lambda: logging.disable(logging.NOTSET))


@pytest.fixture(name="logger_name")
def _logger_name(request: FixtureRequest) -> str:
    """Derive unique name from test file path and test name.

    :param request: pytest fixture.

    :return: Logger name a test function can use.
    """
    return f"{__name__}.{request.node.name}"


@pytest.fixture(name="freeze_time")
def _freeze_time(monkeypatch: MonkeyPatch) -> float:
    """Freeze time for deterministic timestamps. Return the frozen time value.

    :param monkeypatch: pytest fixture.
    """
    mock_seconds = 1576790285.41593
    monkeypatch.setattr("time.time", lambda: mock_seconds)
    return mock_seconds


def _init_logger(name: str, formatter: logging.Formatter) -> logging.Logger:
    """Create a logger for tests."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


@pytest.mark.parametrize("traceback", [True, False])
def test_log_formatter_traceback(capsys: CaptureFixture, logger_name: str, traceback: bool):
    """Test LogFormatter.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    :param traceback: Enable printing traceback.
    """
    log = _init_logger(logger_name, LogFormatter(traceback=traceback))
    generate_log_statements(log, emit_warnings=False)
    output = capsys.readouterr()[0].splitlines()

    expected = [
        "DEBUG: Some debug statements: var",
        "INFO: An info statement.",
        "WARNING: This is a warning statement: 123",
        "ERROR: An error has occurred.",
        "CRITICAL: Critical failure: ERR",
        "ERROR: Here be an exception.",
    ]
    if not traceback:
        assert output == expected
        return

    expected += [
        "Traceback (most recent call last):",
        f'  File "{utils_filename}", line 21, in generate_log_statements',
        '    raise RuntimeError("An exception has occurred.")',
        "RuntimeError: An exception has occurred.",
    ]
    assert output == expected


def test_log_formatter_bells(capsys: CaptureFixture, logger_name: str):
    """Test LogFormatter with bell characters.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    """
    log = _init_logger(logger_name, LogFormatter(bells={logging.WARNING: "\007"}))
    generate_log_statements(log, emit_warnings=False)
    output = capsys.readouterr()[0].splitlines()

    assert "WARNING: This is a warning statement: 123\007" in output
    assert "ERROR: An error has occurred." in output


def test_log_formatter_colors(capsys: CaptureFixture, logger_name: str):
    """Test LogFormatter with colors enabled.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    """
    log = _init_logger(logger_name, LogFormatter(colors=True, traceback=True))
    generate_log_statements(log, emit_warnings=False)
    output = capsys.readouterr()[0].splitlines()

    assert "\033[91mERROR\033[0m: An error has occurred." in output
    assert "Traceback \033[1;36m(most recent call last)\033[0m:" in output


def test_default(capsys: CaptureFixture, logger_name: str):
    """Test default values for arguments.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    """
    log = setup_logging(logger_name=logger_name)
    assert not generate_log_statements(log)
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]

    expected_stdout = [
        "An info statement.",
    ]
    assert stdout == expected_stdout

    expected_stderr = [
        "WARNING: This is a warning statement: 123",
        "ERROR: An error has occurred.",
        "CRITICAL: Critical failure: ERR",
        "ERROR: Here be an exception.",
    ]
    assert stderr == expected_stderr


def test_quiet(capsys: CaptureFixture, logger_name: str):
    """Test quiet.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    """
    log = setup_logging(logger_name=logger_name, verbose=-1)
    assert not generate_log_statements(log)
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]
    assert not stdout
    assert not stderr


@pytest.mark.parametrize("verbose", [1, 2, 3])
def test_verbose(capsys: CaptureFixture, logger_name: str, verbose: int):
    """Test verbose 1 - 3.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    :param verbose: Verbosity level.
    """
    log = setup_logging(logger_name=logger_name, verbose=verbose)
    if verbose == 1:
        assert not generate_log_statements(log)
    else:
        assert generate_log_statements(log) == ["This thing shouldn't happen."]
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]

    expected_stdout = [
        "Some debug statements: var",
        "An info statement.",
    ]
    assert stdout == expected_stdout

    expected_stderr = [
        "WARNING: This is a warning statement: 123",
        "ERROR: An error has occurred.",
        "CRITICAL: Critical failure: ERR",
        "ERROR: Here be an exception.",
    ]
    if verbose == 3:
        expected_stderr += [
            "Traceback (most recent call last):",
            f'  File "{utils_filename}", line 21, in generate_log_statements',
            '    raise RuntimeError("An exception has occurred.")',
            "RuntimeError: An exception has occurred.",
        ]
    assert stderr == expected_stderr


@pytest.mark.parametrize("force_wide,terminal_width", [
    (False, 160),
    (True, 80),
    (True, 160),
])
@pytest.mark.usefixtures("freeze_time")
def test_extended(capsys: CaptureFixture, monkeypatch: MonkeyPatch, logger_name: str, force_wide: bool, terminal_width: int):
    """Test extended formatting.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param logger_name: Module fixture.
    :param force_wide: When user specifies "-ee".
    :param terminal_width: Mock terminal width.
    """
    monkeypatch.setattr("boilerplatepython.logging.get_terminal_size", lambda: type("", (), {"columns": terminal_width}))
    log = setup_logging(logger_name=logger_name, extended=2 if force_wide else 1)
    generate_log_statements(log)
    stdout, stderr = [i.splitlines() for i in capsys.readouterr()]

    expected_stdout = [
        "2019-12-19T21:18:05.415 [INFO    ] generate_log_statements:16: An info statement.",
    ]
    assert stdout == expected_stdout

    expected_stderr = [
        "2019-12-19T21:18:05.415 [WARNING ] do_log:9: This is a warning statement: 123",
        "2019-12-19T21:18:05.415 [ERROR   ] do_log:10: An error has occurred.",
        "2019-12-19T21:18:05.415 [CRITICAL] generate_log_statements:18: Critical failure: ERR",
        "2019-12-19T21:18:05.415 [ERROR   ] generate_log_statements:23: Here be an exception.",
    ]
    assert stderr == expected_stderr


@pytest.mark.usefixtures("freeze_time")
def test_extended_narrow(capsys: CaptureFixture, monkeypatch: MonkeyPatch, logger_name: str):
    """Test extended-narrow formatting.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param logger_name: Module fixture.
    """
    monkeypatch.setattr("boilerplatepython.logging.get_terminal_size", lambda: type("", (), {"columns": 80}))
    log = setup_logging(logger_name=logger_name, extended=1, verbose=1)
    generate_log_statements(log)
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
    assert stderr == expected_stderr


def test_bells(capsys: CaptureFixture, logger_name: str):
    """Test bells forced on.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    """
    log = setup_logging(logger_name=logger_name, verbose=1, bells=True)
    generate_log_statements(log)
    output = [line for s in capsys.readouterr() for line in s.splitlines()]

    expected = [
        "Some debug statements: var",
        "An info statement.",
        "WARNING: This is a warning statement: 123\007\007",
        "ERROR: An error has occurred.\007\007\007",
        "CRITICAL: Critical failure: ERR\007\007\007\007",
        "ERROR: Here be an exception.\007\007\007",
    ]
    assert output[:len(expected)] == expected


@pytest.mark.parametrize("mock_tty", [False, True])
@pytest.mark.parametrize("bells", [None, False, True])
def test_auto_bells(
        capsys: CaptureFixture,
        monkeypatch: MonkeyPatch,
        logger_name: str,
        bells: Optional[bool],
        mock_tty: bool,
):
    """Test automatic bells based on TTY detection.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param logger_name: Module fixture.
    :param bells: None == automatic, False == force off, True == force on.
    :param mock_tty: Mock a tty on stdout.
    """
    if mock_tty:
        monkeypatch.setattr("boilerplatepython.logging.sys_stdout", type("", (), {"isatty": lambda: True}))

    log = setup_logging(logger_name=logger_name, bells=bells)
    generate_log_statements(log)
    output = capsys.readouterr()[1].splitlines()[0]

    if bells is True:
        assert "\007" in output
    elif bells is False:
        assert "\007" not in output
    else:
        if mock_tty:
            assert "\007" in output
        else:
            assert "\007" not in output


def test_colors(capsys: CaptureFixture, logger_name: str):
    """Test colors forced on.

    :param capsys: pytest fixture.
    :param logger_name: Module fixture.
    """
    log = setup_logging(logger_name=logger_name, verbose=3, colors=True)
    generate_log_statements(log)
    output = [line for s in capsys.readouterr() for line in s.splitlines()]

    expected = [
        "Some debug statements: var",
        "An info statement.",
        "\033[33mWARNING\033[0m: This is a warning statement: 123",
        "\033[91mERROR\033[0m: An error has occurred.",
        "\033[91mCRITICAL\033[0m: Critical failure: ERR",
        "\033[91mERROR\033[0m: Here be an exception.",
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
    :param logger_name: Module fixture.
    :param colors: None == automatic, False == force off, True == force on.
    :param mock_tty: Mock a tty on stdout.
    """
    if mock_tty:
        monkeypatch.setattr("boilerplatepython.logging.sys_stdout", type("", (), {"isatty": lambda: True}))

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
