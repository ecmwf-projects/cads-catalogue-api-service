import datetime

from cads_catalogue_api_service.sanity_check import (
    SanityCheckOutput,
    SanityCheckResult,
    SanityCheckStatus,
    get_outputs,
    process,
)


def test_get_outputs() -> None:
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    # Test case: None input
    assert get_outputs(None) is None

    # Test case: Empty list
    assert get_outputs([]) is None

    # Test case: Valid input
    valid_input = [
        {"req_id": "test1", "success": True, "timestamp": timestamp},
        {"req_id": "test2", "success": False, "timestamp": timestamp},
    ]
    result = get_outputs(valid_input)
    assert result is not None
    assert len(result) == 2
    assert result[0].req_id == "test1"
    assert result[0].success is True
    assert result[1].req_id == "test2"
    assert result[1].success is False

    # Test case: Missing required field
    invalid_missing_field = [
        {
            "req_id": "test1",
            # missing success field
            "timestamp": timestamp,
        }
    ]
    assert get_outputs(invalid_missing_field) is None

    # Test case: Wrong type for success field
    invalid_wrong_type = [
        {
            "req_id": "test1",
            "success": "not a boolean",  # wrong type
            "timestamp": timestamp,
        }
    ]
    assert get_outputs(invalid_wrong_type) is None

    # Test case: Invalid timestamp
    invalid_timestamp = [
        {
            "req_id": "test1",
            "success": True,
            "timestamp": "not a datetime",  # wrong type
        }
    ]
    assert get_outputs(invalid_timestamp) is None


def test_process_sanity_check() -> None:
    timestamp = datetime.datetime.now(datetime.timezone.utc)

    # Test case: None or empty list
    assert process(None) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=None,
    )
    assert process([]) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=None,
    )

    # Test case: More than 3 tests
    four_tests = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=False, timestamp=timestamp),
        SanityCheckOutput(req_id="test3", success=False, timestamp=timestamp),
        SanityCheckOutput(req_id="test4", success=False, timestamp=timestamp),
    ]
    assert process(four_tests) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=timestamp,
    )

    # Test case: 1 test, successful
    one_test_success = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp)
    ]
    assert process(one_test_success) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=timestamp,
    )

    # Test case: 1 test, failed
    one_test_failed = [
        SanityCheckOutput(req_id="test1", success=False, timestamp=timestamp)
    ]
    assert process(one_test_failed) == SanityCheckResult(
        status=SanityCheckStatus.down,
        timestamp=timestamp,
    )

    # Test case: 2 tests, all successful
    two_tests_all_success = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=True, timestamp=timestamp),
    ]
    assert process(two_tests_all_success) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=timestamp,
    )

    # Test case: 2 tests, 1 successful
    two_tests_one_success = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=False, timestamp=timestamp),
    ]
    assert process(two_tests_one_success) == SanityCheckResult(
        status=SanityCheckStatus.warning,
        timestamp=timestamp,
    )

    # Test case: 2 tests, none successful
    two_tests_none_success = [
        SanityCheckOutput(req_id="test1", success=False, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=False, timestamp=timestamp),
    ]
    assert process(two_tests_none_success) == SanityCheckResult(
        status=SanityCheckStatus.down,
        timestamp=timestamp,
    )

    # Test case: 3 tests, all successful
    three_tests_all_success = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test3", success=True, timestamp=timestamp),
    ]
    assert process(three_tests_all_success) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=timestamp,
    )

    # Test case: 3 tests, 2 successful
    three_tests_two_success = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test3", success=False, timestamp=timestamp),
    ]
    assert process(three_tests_two_success) == SanityCheckResult(
        status=SanityCheckStatus.available,
        timestamp=timestamp,
    )

    # Test case: 3 tests, 1 successful
    three_tests_one_success = [
        SanityCheckOutput(req_id="test1", success=True, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=False, timestamp=timestamp),
        SanityCheckOutput(req_id="test3", success=False, timestamp=timestamp),
    ]
    assert process(three_tests_one_success) == SanityCheckResult(
        status=SanityCheckStatus.warning,
        timestamp=timestamp,
    )

    # Test case: 3 tests, none successful
    three_tests_none_success = [
        SanityCheckOutput(req_id="test1", success=False, timestamp=timestamp),
        SanityCheckOutput(req_id="test2", success=False, timestamp=timestamp),
        SanityCheckOutput(req_id="test3", success=False, timestamp=timestamp),
    ]
    assert process(three_tests_none_success) == SanityCheckResult(
        status=SanityCheckStatus.down,
        timestamp=timestamp,
    )
