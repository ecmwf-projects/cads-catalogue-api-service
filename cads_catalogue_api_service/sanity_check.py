import datetime
from typing import Any

import pydantic
import structlog
from pydantic import BaseModel

from cads_catalogue_api_service import config, models

logger = structlog.getLogger(__name__)

SANITY_CHECK_MAX_ENTRIES = 3


class SanityCheckOutput(BaseModel):
    """Individual sanity check test structure."""

    req_id: str
    success: bool
    started_at: datetime.datetime
    finished_at: datetime.datetime


# Rules mapping for determining status
# Format: {total_tests: {successful_tests: status}}
status_rules = {
    1: {
        0: models.stac.SanityCheckStatus.DOWN,
        1: models.stac.SanityCheckStatus.AVAILABLE,
    },
    2: {
        0: models.stac.SanityCheckStatus.DOWN,
        1: models.stac.SanityCheckStatus.WARNING,
        2: models.stac.SanityCheckStatus.AVAILABLE,
    },
    3: {
        0: models.stac.SanityCheckStatus.DOWN,
        1: models.stac.SanityCheckStatus.WARNING,
        2: models.stac.SanityCheckStatus.AVAILABLE,
        3: models.stac.SanityCheckStatus.AVAILABLE,
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
) -> models.stac.CadsSanityCheck:
    """Process the sanity check results and determine the status.

    Calculates the status based on the following rules:

    1. If sanity_check is None or empty, status is "unknown".
    2. If the last check is older than `SANITY_CHECK_VALIDITY_DURATION`, status is "expired".
    3. If sanity_check has more than 3 checks, only last 3 checks are taken into account.
    4. For 1 checks:
       - If successful, status is "available"
       - If failed, status is "down"
    5. For 2 checks:
       - If 2 tests succeeded, status is "available"
       - If 1 test succeeded, status is "warning"
       - If 0 tests succeeded, status is "down"
    6. For 3 checks:
       - If 3 or 2 tests succeeded, status is "available"
       - If 1 test succeeded, status is "warning"
       - If 0 tests succeeded, status is "down"

    Args:
        sanity_check: List of test results, each containing a "success" boolean. Only first
            SANITY_CHECK_MAX_ENTRIES are considered for status calculation.

    Returns
    -------
        A dict with "status" ("available", "warning", "down" or "unknown") and "timestamp"
        (from the first check, if available)
    """
    # Default status for empty checks
    if not sanity_check:
        return models.stac.CadsSanityCheck(
            status=models.stac.SanityCheckStatus.UNKNOWN, timestamp=None
        )

    # Just take into account latest X tests (tests are sorted descending by finished_at)
    sanity_check = sanity_check[:SANITY_CHECK_MAX_ENTRIES]

    # Extract timestamp from the latest test
    latest_timestamp = sanity_check[0].finished_at

    # Expired status
    validity_duration = config.settings.sanity_check_validity_duration
    if validity_duration and latest_timestamp:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now - latest_timestamp > datetime.timedelta(minutes=validity_duration):
            return models.stac.CadsSanityCheck(
                status=models.stac.SanityCheckStatus.EXPIRED, timestamp=latest_timestamp
            )

    # Count successful tests
    successful_tests = sum(1 for test in sanity_check if test.success)
    total_tests = len(sanity_check)

    # Get status based on rules or default to "available"
    status = status_rules.get(total_tests, {}).get(
        successful_tests, models.stac.SanityCheckStatus.AVAILABLE
    )

    return models.stac.CadsSanityCheck(status=status, timestamp=latest_timestamp)
