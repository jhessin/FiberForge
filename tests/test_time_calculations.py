from datetime import time, timedelta
from job_docs import JobDoc


class TestDoc(JobDoc):
    pass


def test_total_time_basic():
    d = TestDoc()
    d.start = time(8, 0)
    d.end = time(10, 0)

    assert d.total_time == timedelta(hours=2)


def test_total_time_wraps_midnight():
    d = TestDoc()
    d.start = time(23, 0)
    d.end = time(1, 0)

    assert d.total_time == timedelta(hours=2)


def test_total_time_with_lunch():
    d = TestDoc()
    d.start = time(8, 0)
    d.end = time(12, 0)
    d.lunch_time = timedelta(hours=1)

    assert d.total_time == timedelta(hours=3)
