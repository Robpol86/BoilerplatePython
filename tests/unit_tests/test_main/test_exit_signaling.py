"""Tests."""
import signal

import pytest

from boilerplatepython.__main__ import ExitSignaling


def test():
    """Test."""
    exit_signaling = ExitSignaling()
    assert exit_signaling.exit_code == 0

    with pytest.raises(SystemExit) as exc:
        exit_signaling.exit(signal.SIGTERM, None)

    assert exc.value.code == 143
