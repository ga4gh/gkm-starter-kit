from pathlib import Path

import pytest
import requests


def pytest_addoption(parser):
    """Add custom commands to pytest invocation.

    See https://docs.pytest.org/en/8.1.x/reference/reference.html#parser
    """
    parser.addoption(
        "--verbose-logs",
        action="store_true",
        default=False,
        help="show noisy module logs",
    )


def pytest_configure(config):
    """Configure pytest setup."""
    # add noisy logging libraries.
    if not config.getoption("--verbose-logs"):
        pass


@pytest.fixture(autouse=True)
def block_live_network(monkeypatch):
    """Fail tests that accidentally attempt a live HTTP request."""

    def reject_request(*_args, **_kwargs):
        message = "Live network requests are not allowed in tests"
        raise AssertionError(message)

    monkeypatch.setattr(requests.sessions.Session, "request", reject_request)


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide Path instance pointing to test data directory"""
    return Path(__file__).parent / "data"
