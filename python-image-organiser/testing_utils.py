from unittest.mock import Mock
from collections import Counter


def assert_has_logs(actual_logs: list, logs: list):
    """ Assert that logs is contained within actual logs, including duplicates and order not being important """
    log_counts = Counter(logs)
    assert (log_counts & Counter(actual_logs)) == log_counts, f"Logs not found.\nExpected: {logs}\nActual: {actual_logs}\nMissing:{list(set(logs)-set(actual_logs))}"


def assert_not_logged(actual_logs: list, logs: list):
    for log in logs:
        if log in actual_logs:
            return False
    return True