"""Tests."""
import argparse
import re
from typing import List

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from boilerplatepython.__main__ import WideHelpFormatter


def get_actual(output: str) -> List[str]:
    """Process argparse help output into list of optional arguments."""
    text_block = output.split("optional arguments:")[1].strip()
    stripped_lines = [line.strip() for line in text_block.splitlines()]
    pruned_lines = [line for line in stripped_lines if line.startswith("-")]
    arguments = [re.match(r"[^,\s]+", line)[0] for line in pruned_lines]
    return arguments


def test_sort(capsys: CaptureFixture):
    """Test that optional arguments are sorted correctly.

    :param capsys: pytest fixture.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description="Test.", formatter_class=WideHelpFormatter)
    # Simple A and B case mix.
    parser.add_argument("-B", "--option-upper-b", help="option B upper case")
    parser.add_argument("-A", "--option-upper-a", help="option A upper case")
    parser.add_argument("-b", "--option-lower-b", help="option B lower case")
    parser.add_argument("-a", "--option-lower-a", help="option A lower case")
    # No short and no long.
    parser.add_argument("-d", help="no long alias")
    parser.add_argument("--c-option", help="no short alias")
    # Group.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-10", action="store_true", help="help text")
    group.add_argument("-X", action="store_true", help="help text")
    group.add_argument("-1", action="store_true", help="help text")
    group.add_argument("-J", action="store_true", help="help text")
    group.add_argument("-3", action="store_true", help="help text")
    group.add_argument("-20", action="store_true", help="help text")
    group.add_argument("-2", action="store_true", help="help text")
    group.add_argument("-w", action="store_true", help="help text")
    group.add_argument("-t", action="store_true", help="help text")

    # Run.
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    stdout, stderr = capsys.readouterr()
    assert not stderr
    actual = get_actual(stdout)

    # Test.
    expected = [
        "-1",
        "-2",
        "-3",
        "-10",
        "-20",
        "-a",
        "-A",
        "-b",
        "-B",
        "--c-option",
        "-d",
        "-h",
        "-J",
        "-t",
        "-w",
        "-X",
    ]
    assert actual == expected


@pytest.mark.parametrize("args", (["--help"], ["a", "--help"], ["b", "--help"]))
def test_with_sub_parser(capsys: CaptureFixture, args: List[str]):
    """Test with sub-parser present.

    :param capsys: pytest fixture.
    :param args: Test arguments to pass to the parser.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description="Test.", formatter_class=WideHelpFormatter)
    parser.add_argument("-V", "--version", action="version", version="0.0.0", help="help text")
    sub_parsers = parser.add_subparsers(dest="sub", required=True, help="help text")
    sub1_parser = sub_parsers.add_parser(name="a", formatter_class=parser.formatter_class, help="help text")
    sub1_parser.add_argument("-A", action="store_true", help="help text")
    sub1_parser.add_argument("-a", action="store_true", help="help text")
    sub2_parser = sub_parsers.add_parser(name="b", formatter_class=parser.formatter_class, help="help text")
    sub2_parser.add_argument("-A", action="store_true", help="help text")
    sub2_parser.add_argument("-a", action="store_true", help="help text")

    # Run.
    with pytest.raises(SystemExit):
        parser.parse_args(args)
    stdout, stderr = capsys.readouterr()
    assert not stderr
    actual = get_actual(stdout)

    # Test.
    if len(args) == 1:
        expected = ["-h", "-V"]
    else:
        expected = ["-a", "-A", "-h"]
    assert actual == expected


@pytest.mark.parametrize("mode", ["term_narrow", "term_wide", "env", "arg"])
def test_width(monkeypatch: MonkeyPatch, mode: str):
    """Test width detection.

    :param monkeypatch: pytest fixture.
    :param mode: source of test value.
    """
    if mode == "term_narrow":
        monkeypatch.setattr("boilerplatepython.__main__.get_terminal_size", lambda: type("", (), {"columns": 81}))
        expected = 81
    elif mode == "term_wide":
        monkeypatch.setattr("boilerplatepython.__main__.get_terminal_size", lambda: type("", (), {"columns": 581}))
        expected = WideHelpFormatter.MAX_DEFAULT_WIDTH
    elif mode == "env":
        monkeypatch.setattr(WideHelpFormatter, "OS_ENVIRON", dict(COLUMNS="82"))
        expected = 82
    else:
        expected = None

    # Run.
    if mode == "arg":
        fmt = WideHelpFormatter("test", width=200)
        expected = 200
    else:
        fmt = WideHelpFormatter("test")

    # Test.
    assert fmt.width == expected
