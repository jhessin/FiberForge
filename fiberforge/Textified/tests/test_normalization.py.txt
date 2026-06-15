from job_docs import JobDoc, Can, Sheath
from utils import FiberRun


class TestDoc(JobDoc):
    """Minimal concrete subclass for testing."""

    pass


def test_cans_involved_normalizes_single():
    c = Can("C1")
    d = TestDoc()
    d.cans_involved = c

    assert d._cans_involved == (c,)


def test_cans_involved_normalizes_iterable():
    c1, c2 = Can("A"), Can("B")
    d = TestDoc()
    d.cans_involved = [c1, c2]

    assert d._cans_involved == (c1, c2)


def test_removing_normalizes_mixed():
    c = Can("C1")
    s = Sheath("S1")
    d = TestDoc()
    d.removing = [c, s]

    assert d._removing == (c, s)


def test_fiber_runs_normalizes_single():
    r = FiberRun("Run1")
    d = TestDoc()
    d.fiber_runs = r

    assert isinstance(d._fiber_runs, tuple)
    assert len(d._fiber_runs) == 1
    assert d._fiber_runs[0] is r
    assert d._fiber_runs[0].name.startswith("Run1")
