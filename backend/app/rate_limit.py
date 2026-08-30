from collections import defaultdict
from datetime import datetime, timedelta, timezone

WINDOW = timedelta(hours=1)
MAX_REQUESTS_PER_WINDOW = 3

# In-process only — fine for a single Render instance, per Global Constraints.
# Would need a shared store (e.g. Redis) if this ever ran on multiple instances.
_request_log: dict[str, list[datetime]] = defaultdict(list)


def is_rate_limited(client_ip: str, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    cutoff = now - WINDOW

    recent = [ts for ts in _request_log[client_ip] if ts > cutoff]
    _request_log[client_ip] = recent

    if len(recent) >= MAX_REQUESTS_PER_WINDOW:
        return True

    recent.append(now)
    return False


def reset_rate_limits() -> None:
    """Test helper: clear all tracked request history."""
    _request_log.clear()