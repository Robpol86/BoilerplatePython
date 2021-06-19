"""Logging."""
import logging
import sys
import warnings
from shutil import get_terminal_size
from typing import Optional

LOG_FORMAT_DEFAULT = (
    "%(asctime)s "
    "[%(levelcolor1)s%(levelname)-8s%(levelcolor2)s] "
    "%(colorA1)s%(funcName)s:%(lineno)s:%(colorA2)s "
    "%(message)s"
)
LOG_FORMAT_NARROW = "%(asctime)s %(levelcolor1)s%(shortlevelname)s%(levelcolor2)s: %(message)s"
STDOUT_ISATTY = sys.stdout.isatty()


# pylint: disable=too-few-public-methods
class InfoLogFilter(logging.Filter):
    """Filter out non-info and non-debug logging statements."""

    def filter(self, record: logging.LogRecord) -> int:
        """Apply filter."""
        return int(record.levelno <= logging.INFO)


class LogFormatter(logging.Formatter):
    """Enhanced logging formatter for the project.

    * Lets caller disable tracebacks from being emitted from log.exception(), rendering them equivalent to log.error().
    * Preset format strings as class variables.
    * Custom timestamps.
    * Add color fields.
    """

    COLOR_CODES = {
        logging.CRITICAL: [91, 0],
        logging.ERROR: [91, 0],
        logging.WARNING: [33, 0],
        logging.INFO: [36, 0],
        logging.DEBUG: [95, 0],
        "colorA": [2, 22],
    }
    SHORT_LEVEL_NAMES = {
        logging.CRITICAL: "CRIT",
        logging.ERROR: "ERRO",
        logging.WARNING: "WARN",
        logging.INFO: "INFO",
        logging.DEBUG: "DBUG",
        logging.NOTSET: "NSET",
    }
    default_time_format = "%Y-%m-%dT%H:%M:%S"
    default_time_format_narrow = "%dT%H:%M:%S"
    default_msec_format = "%s.%03d"

    def __init__(
        self,
        fmt: Optional[str] = None,
        force_wide: bool = False,
        colors: bool = False,
        traceback: bool = True,
        **kwargs,
    ):
        """Class constructor.

        :param fmt: Format string.
        :param force_wide: Don't automatically use narrow format in narrow terminals.
        :param colors: Add color escape sequences to color formatter fields.
        :param traceback: Print tracebacks for logging.exception().
        """
        if fmt is None:
            if force_wide or get_terminal_size().columns > 110:
                fmt = LOG_FORMAT_DEFAULT
            else:
                fmt = LOG_FORMAT_NARROW
                self.default_time_format = self.default_time_format_narrow
        self.colors = colors
        self.traceback = traceback
        self.color_codes_flattened = {
            key: [f"\033[{color1}m" if colors else "", f"\033[{color2}m" if colors else ""]
            for key, (color1, color2) in self.COLOR_CODES.items()
        }
        super().__init__(fmt=fmt, **kwargs)

    def formatMessage(self, record: logging.LogRecord) -> str:  # noqa: N802
        """Add custom formatter fields."""
        color_codes_flattened = self.color_codes_flattened
        record.levelcolor1, record.levelcolor2 = color_codes_flattened.get(record.levelno, ["", ""])
        record.colorA1, record.colorA2 = color_codes_flattened.get("colorA", ["", ""])
        record.shortlevelname = self.SHORT_LEVEL_NAMES.get(record.levelno, "????")
        return super().formatMessage(record)

    def formatException(self, ei) -> str:  # noqa: N802
        """Conditionally hide tracebacks or syntax highlight them."""
        if not self.traceback:
            return ""
        if not self.colors:
            return super().formatException(ei)
        try:
            # pylint: disable=import-outside-toplevel
            from IPython.core.ultratb import ColorTB
        except ImportError:
            return super().formatException(ei)
        return ColorTB().text(*ei)


def setup_logging(
    colors: bool = False,
    force_wide: bool = False,
    verbose: int = 0,
    logger_name: Optional[str] = None,
    **kwargs,
) -> logging.Logger:
    """Initialize console logging.

    Info and below go to stdout, others go to stderr.

    :param colors: Auto if None depending on stdout being a tty.
    :param force_wide: Don't automatically use narrow format in narrow terminals.
    :param verbose: Verbosity of logging (<0: quiet, 0: normal, >=1: DEBUG statements, >=2: warnings, >=3: tracebacks).
    :param logger_name: Which logger to set handlers to (used for testing, default is root logger).
    :param kwargs: Passed to LogFormatter.

    :return: The root logger (used for testing).
    """
    # Suppress warnings.
    if verbose < 2:
        warnings.filterwarnings("ignore")

    # Disable logging if quiet.
    logger = logging.getLogger(logger_name)
    if verbose < 0:
        logging.disable(logging.CRITICAL)
        return logger
    logger.disabled = False
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Automatic colors.
    if colors is None:
        colors = STDOUT_ISATTY

    # Initialize stream logging.
    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setFormatter(LogFormatter(force_wide=force_wide, colors=colors, traceback=verbose >= 3, **kwargs))
    handler_stdout.setLevel(logging.DEBUG)
    handler_stdout.addFilter(InfoLogFilter())
    logger.addHandler(handler_stdout)

    handler_stderr = logging.StreamHandler(sys.stderr)
    handler_stderr.setFormatter(handler_stdout.formatter)
    handler_stderr.setLevel(logging.WARNING)
    logger.addHandler(handler_stderr)

    return logger
