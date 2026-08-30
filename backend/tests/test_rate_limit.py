from datetime import datetime, timezone

from app.rate_limit import is_rate_limited, reset_rate_limits


def _dt(*args):
    return datetime(*args, tzinfo=timezone.utc)


def setup_function():
    reset_rate_limits()


def test_allows_requests_under_the_limit():
    for _ in range(3):
        assert is_rate_limited("1.2.3.4", now=_dt(2026, 1, 1)) is False


def test_blocks_requests_over_the_limit():
    for _ in range(3):
        is_rate_limited("1.2.3.4", now=_dt(2026, 1, 1))

    assert is_rate_limited("1.2.3.4", now=_dt(2026, 1, 1)) is True


def test_different_ips_are_tracked_independently():
    for _ in range(3):
        is_rate_limited("1.2.3.4", now=_dt(2026, 1, 1))

    assert is_rate_limited("5.6.7.8", now=_dt(2026, 1, 1)) is False


def test_old_requests_fall_out_of_the_window():
    for _ in range(3):
        is_rate_limited("1.2.3.4", now=_dt(2026, 1, 1, 0, 0))

    assert is_rate_limited("1.2.3.4", now=_dt(2026, 1, 1, 2, 0)) is False