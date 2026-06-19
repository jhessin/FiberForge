from textual.widgets import Static
from fiberforge.models import Job


class JobDetails(Static):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__("", *args, **kwargs)
        self.job: Job | None = None

    def update_job(self, job: Job) -> None:
        self.job = job
        meta = job.meta
        lines = [
            f"ID:        {job.id}",
            f"Name:      {meta.job_name or '—'}",
            f"Type:      {meta.job_type or '—'}",
            f"Task:      {meta.task_name or '—'}",
            f"Company:   {meta.company_name or '—'}",
            f"Region:    {meta.region or '—'}",
            f"Address:   {meta.address or '—'}",
            f"Revision:  {meta.revision_number}",
            "",
            f"Total Time: {job.timeclock.total_time}",
            "",
            "Notes:",
            meta.notes or "No Notes",
        ]
        self.update("\n".join(lines))
