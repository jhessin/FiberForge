from job_docs import JobDoc


class TestDoc(JobDoc):
    pass


def test_cfat_disabled():
    d = TestDoc()
    d.job_type = "Design"
    d.region = "MWR"
    d.disable_cfat = True

    assert d.cfat_check() is False


def test_cfat_requires_fields():
    d = TestDoc()
    d.job_type = "Design"
    d.region = "MWR"
    d.mux = "MUX1"
    d.mux_types = ["TYPE1"]
    d.mux_address = "ADDR"

    assert d.cfat_check() is True
