from job_docs import JobDoc


class TestDoc(JobDoc):
    pass


def test_file_generation_basic(capsys):
    d = TestDoc()
    d.job_name = "JB123"
    d.job_type = "Asbuilt"
    d.endsites = ["TNM1"]
    d.nodes = ["NODE1"]
    d.region = "MWR"
    d.state = "NE"
    d.company_name = "TestCo"
    d.task_name = "Task"
    d.address = "123 St"

    d.show_files()
    out = capsys.readouterr().out

    assert "JB123_TNM1_BM_F_A.pdf" in out
