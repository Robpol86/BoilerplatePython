"""Utilities used by tests."""
import logging
import warnings
from typing import List


def do_log(log: logging.Logger):
    """Log two statements, for testing with short function names in debug logging."""
    log.warning("This is a warning statement: %d", 123)
    log.error("An error has occurred.")


def generate_log_statements(log: logging.Logger, emit_warnings: bool = True) -> List[str]:
    """Write some test logging statements to the logger."""
    log.debug("Some debug statements: %s", "var")
    log.info("An info statement.")
    do_log(log)
    log.critical("Critical failure: %s", "ERR")

    try:
        raise RuntimeError("An exception has occurred.")
    except RuntimeError:
        log.exception("Here be an exception.")

    if not emit_warnings:
        return []

    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.warn("This thing shouldn't happen.")

    return [w.message.args[0] for w in recorded_warnings]
