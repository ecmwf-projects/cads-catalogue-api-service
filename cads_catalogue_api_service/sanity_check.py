import datetime
from enum import Enum
from typing import Any

import pydantic
import structlog
from pydantic import BaseModel

logger = structlog.getLogger(__name__)

SANITY_CHECK_MAX_ENTRIES = 3


class SanityCheckStatus(str, Enum):
    available = "available"
    warning = "warning"
    down = "down"


class SanityCheckOutput(BaseModel):
    """Individual sanity check test structure."""

    req_id: str
    success: bool
    started_at: datetime.datetime
    finished_at: datetime.datetime


class SanityCheckResult(BaseModel):
    """Result of processing sanity checks."""

    status: SanityCheckStatus
    timestamp: datetime.datetime | None

    def dict(self, *args, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(*args, **kwargs)
        if data["timestamp"] is not None:
            data["timestamp"] = data["timestamp"].isoformat()
        return data


# Rules mapping for determining status
# Format: {total_tests: {successful_tests: status}}
status_rules = {
    1: {0: SanityCheckStatus.down, 1: SanityCheckStatus.available},
    2: {
        0: SanityCheckStatus.down,
        1: SanityCheckStatus.warning,
        2: SanityCheckStatus.available,
    },
    3: {
        0: SanityCheckStatus.down,
        1: SanityCheckStatus.warning,
        2: SanityCheckStatus.available,
        3: SanityCheckStatus.available,
    },
}


def get_outputs(
    raw_sanity_checks: list[dict[str, Any]] | None,
) -> list[SanityCheckOutput] | None:
    """Convert raw sanity check data from database to SanityCheckOutput objects.

    If conversion fails, returns None.
    """
    if not raw_sanity_checks:
        return None

    try:
        return [
            SanityCheckOutput(
                req_id=output["req_id"],
                success=output["success"],
                started_at=output["started_at"],
                finished_at=output["finished_at"],
            )
            for output in raw_sanity_checks
        ]
    except (KeyError, pydantic.ValidationError) as e:
        logger.error("Error converting sanity check data", error=e)
        return None


def process(
    sanity_check: list[SanityCheckOutput] | None,
) -> SanityCheckResult:
    """Process the sanity check results and determine the status.

    Calculates the status based on the following rules:

    1. If sanity_check is None or empty or has more than 3 tests, status is "available".
    2. For 1 test:
       - If successful, status is "available"
       - If failed, status is "down"
    3. For 2 tests:
       - If 2 tests succeeded, status is "available"
       - If 1 test succeeded, status is "warning"
       - If 0 tests succeeded, status is "down"
    4. For 3 tests:
       - If 3 or 2 tests succeeded, status is "available"
       - If 1 test succeeded, status is "warning"
       - If 0 tests succeeded, status is "down"

    Args:
        sanity_check: List of test results, each containing a "success" boolean. Only first
            SANITY_CHECK_MAX_ENTRIES are considered for status calculation.

    Returns
    -------
        Dict with "status" ("available", "warning", or "down") and
        "timestamp" (from the first test if available)
    """
    # Default status for empty checks
    if not sanity_check:
        return SanityCheckResult(status=SanityCheckStatus.available, timestamp=None)

    # Just take into account latest X tests (tests are sorted descending by finished_at)
    sanity_check = sanity_check[:SANITY_CHECK_MAX_ENTRIES]

    # Extract timestamp from the latest test
    timestamp = sanity_check[0].finished_at

    # Count successful tests
    successful_tests = sum(1 for test in sanity_check if test.success)
    total_tests = len(sanity_check)

    # Get status based on rules or default to "available"
    status = status_rules.get(total_tests, {}).get(
        successful_tests, SanityCheckStatus.available
    )

    return SanityCheckResult(status=status, timestamp=timestamp)
