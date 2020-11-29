"""Tests."""
import logging
import sys

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from boilerplatepython.logging import LogFormatter
from .utils import __file__ as utils_filename, generate_log_statements


def _init_logger(name: str, formatter: logging.Formatter) -> logging.Logger:
    """Create a logger for tests."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


@pytest.mark.parametrize("force_wide,terminal_width", [
    (False, 160),
    (True, 80),
    (True, 160),
])
@pytest.mark.usefixtures("freeze_time")
def test_wide(capsys: CaptureFixture, monkeypatch: MonkeyPatch, logger_name: str, force_wide: bool, terminal_width: int):
    """Test.

    :param capsys: pytest fixture.
    :param monkeypatch: pytest fixture.
    :param logger_name: conftest fixture.
    :param force_wide: Don't automatically use narrow formatting.
    :param terminal_width: Mock terminal width.
    """
    monkeypatch.setattr("boilerplatepython.logging.get_terminal_size", lambda: type("", (), {"columns": terminal_width}))
    log = _init_logger(logger_name, LogFormatter(force_wide=force_wide, traceback=False))
    generate_log_statements(log)
    output = capsys.readouterr()[0].splitlines()

    expected = [
        "2019-12-19T21:18:05.415 [DEBUG   ] generate_log_statements:15: Some debug statements: var",
        "2019-12-19T21:18:05.415 [INFO    ] generate_log_statements:16: An info statement.",
        "2019-12-19T21:18:05.415 [WARNING ] do_log:9: This is a warning statement: 123",
        "2019-12-19T21:18:05.415 [ERROR   ] do_log:10: An error has occurred.",
        "2019-12-19T21:18:05.415 [CRITICAL] generate_log_statements:18: Critical failure: ERR",
        "2019-12-19T21:18:05.415 [ERROR   ] generate_log_statements:23: Here be an exception.",
    ]
    assert output == expected


@pytest.mark.parametrize("traceback", [True, False])
@pytest.mark.usefixtures("freeze_time")
def test_traceback(capsys: CaptureFixture, logger_name: str, traceback: bool):
    """Test.

    :param capsys: pytest fixture.
    :param logger_name: conftest fixture.
    :param traceback: Enable printing traceback.
    """
    log = _init_logger(logger_name, LogFormatter(traceback=traceback))
    generate_log_statements(log, emit_warnings=False)
    output = capsys.readouterr()[0].splitlines()

    expected = [
        "19T21:18:05.415 DBUG: Some debug statements: var",
        "19T21:18:05.415 INFO: An info statement.",
        "19T21:18:05.415 WARN: This is a warning statement: 123",
        "19T21:18:05.415 ERRO: An error has occurred.",
        "19T21:18:05.415 CRIT: Critical failure: ERR",
        "19T21:18:05.415 ERRO: Here be an exception.",
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


@pytest.mark.usefixtures("freeze_time")
def test_colors(capsys: CaptureFixture, logger_name: str):
    """Test.

    :param capsys: pytest fixture.
    :param logger_name: conftest fixture.
    """
    log = _init_logger(logger_name, LogFormatter(colors=True, traceback=True))
    generate_log_statements(log, emit_warnings=False)
    output = capsys.readouterr()[0].splitlines()

    assert "19T21:18:05.415 \033[91mERRO\033[0m: An error has occurred." in output
    assert "Traceback \033[1;36m(most recent call last)\033[0m:" in output
