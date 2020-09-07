"""CLI entry point."""
import argparse
import logging
import os
import signal
import sys
from shutil import get_terminal_size
from types import FrameType
from typing import Iterable, Tuple

from boilerplatepython import __version__
from boilerplatepython.conf import Config
from boilerplatepython.logging import setup_logging


class ExitSignaling:
    """Gracefully exit on OS signals.

    :ivar exit_code: Exit with this code.
    """

    def __init__(self, initial_exit_code: int = 0):
        """Class constructor."""
        self.exit_code = initial_exit_code

    def exit(self, signum: int, _: FrameType):
        """Gracefully stop the program."""
        self.exit_code = 128 + signum

        # Quit.
        logging.getLogger(__name__).info("QUITTING %d", self.exit_code)
        sys.exit(self.exit_code)

    def register(self):
        """Register signal handlers."""
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)


class WideHelpFormatter(argparse.HelpFormatter):
    """Custom formatting for the CLI help menu.

    * Default total width set to terminal width up to 120 characters.
    * Widens the argument list first column to avoid ugly line wrapping.
    * Sort optional arguments list.
    """

    MAX_DEFAULT_WIDTH = 120
    os_environ = os.environ  # For testing.

    def __init__(self, prog, indent_increment=2, max_help_position=31, width=None):
        """Class constructor."""
        if width is None:
            try:
                width = int(self.os_environ["COLUMNS"])  # Copied from HelpFormatter code.
            except (KeyError, ValueError):
                width = min(get_terminal_size().columns, self.MAX_DEFAULT_WIDTH)
        super().__init__(prog, indent_increment, max_help_position, width)

    @property
    def width(self) -> int:
        """Public getter method for private attribute."""
        return self._width

    @staticmethod
    def rank_argument_lower_first(action: argparse.Action) -> Tuple[float, str, str]:
        """Rank arguments alphabetically lower-case first.

        https://stackoverflow.com/questions/33161059/how-to-sort-a-list-in-python-to-make-lowercase-precede-uppercase
        """
        try:
            value = action.option_strings[0].lstrip("-")
        except IndexError:
            # Not an option, probably a sub-parser.
            return float("-Inf"), "", ""

        try:
            numeric = float(value)
        except ValueError:
            numeric = float("Inf")

        return numeric, value.casefold(), value.swapcase()

    def add_arguments(self, actions):
        """Sort arguments when adding them."""
        super().add_arguments(sorted(actions, key=self.rank_argument_lower_first))


def cli(args: Iterable[str] = None) -> Config:
    """Parse arguments from the CLI.

    :param args: Arguments to parse (default: sys.argv[1:]).

    :return: Parsed configuration.
    """
    # Initialize the global parser.
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        formatter_class=WideHelpFormatter,
        description="Example program. Description goes here.",
    )
    parser.add_argument("-b", "--bell", metavar="WHEN", choices=["never", "always", "auto"], default="auto",
                        help="audible alerts on warnings and errors if tty (never, always, auto; default:\u00A0%(default)s)")
    parser.add_argument("-c", "--color", metavar="WHEN", choices=["never", "always", "auto"], default="auto",
                        help="print colors in log statements and output (never, always, auto; default:\u00A0%(default)s)")
    parser.add_argument("-e", "--extended-output", action="count", default=0,
                        help="timestamps and more, second -e forces wide formatting")
    parser.add_argument("-V", "--version", action="version", version=__version__, help="print the program version and exit")
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-q", "--quiet", action="store_true", help="quiet output, only print errors")
    verbosity_group.add_argument("-v", "--verbose", action="count", default=0,
                                 help="verbose mode, multiple -v increase the verbosity")

    # Parse and return.
    parsed = parser.parse_args(args if args is not None else sys.argv[1:])
    return Config(
        # Global options.
        prog=parser.prog,
        bell=dict(never=False, always=True, auto=None)[parsed.bell],
        color=dict(never=False, always=True, auto=None)[parsed.color],
        extended=parsed.extended_output,
        quiet=parsed.quiet,
        verbose=parsed.verbose,
    )


def main():
    """CLI entry point."""
    exit_signaling = ExitSignaling()
    exit_signaling.register()  # Properly handle Control+C.

    config = cli()
    setup_logging(
        bells=config.bell,
        colors=config.color,
        extended=config.extended,
        verbose=-1 if config.quiet else config.verbose,
    )

    # Run.
    print("Hello World")

    # Exit.
    sys.exit(exit_signaling.exit_code)


if __name__ == "__main__":
    main()
