from job_docs import JobDoc, Can, Sheath
from utils import FiberRun


class TestDoc(JobDoc):
    pass


def test_show_cans(capsys):
    c = Can("C1", attached_sheaths=(Sheath("S1"),))
    d = TestDoc()
    d.cans_involved = c

    d.show_cans()
    out = capsys.readouterr().out

    assert "C1" in out


def test_show_runs_single(capsys):
    r = FiberRun("Run1")
    d = TestDoc()
    d.fiber_runs = r

    d.show_runs()
    out = capsys.readouterr().out

    assert "Run1" in out
