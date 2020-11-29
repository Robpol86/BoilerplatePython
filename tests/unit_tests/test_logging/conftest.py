"""pytest fixtures and hooks."""
import os
import time

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(autouse=True, scope="session")
def _setup():
    """Run for all tests."""
    os.environ["TZ"] = "UTC"
    time.tzset()


@pytest.fixture()
def logger_name(request: FixtureRequest) -> str:
    """Derive unique name from test file path and test name.

    :param request: pytest fixture.

    :return: Logger name a test function can use.
    """
    return f"{__name__}.{request.node.module.__name__}.{request.node.name}"


@pytest.fixture()
def freeze_time(monkeypatch: MonkeyPatch) -> float:
    """Freeze time for deterministic timestamps. Return the frozen time value.

    :param monkeypatch: pytest fixture.
    """
    mock_seconds = 1576790285.41593
    monkeypatch.setattr("time.time", lambda: mock_seconds)
    return mock_seconds
