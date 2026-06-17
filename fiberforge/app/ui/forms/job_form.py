# fiberforge/ui/forms/job_form.py

from __future__ import annotations

from textual.screen import ModalScreen
from textual.widgets import Button, Select

from fiberforge.models import (
    Job,
)
from .custom_fields import InputField


class JobFormScreen(ModalScreen[Job]):

    def compose(self):
        return [
            InputField("Job ID", name="id", required=True),
            InputField("Job Name", name="job_name", required=True),
            InputField("Details", name="details"),
            InputField("Task Name", name="task_name", required=True),
            InputField("Company", name="company_name", required=True),
            InputField("Address", name="address", required=True),
            InputField("Latitude", name="lat"),
            InputField("Longitude", name="long"),
            InputField("CLLI", name="clli"),
            # Select widgets
            Select(
                name="region",
                options=[("MWR", "MWR"), ("BSR", "BSR"), ("HOUSTON", "HOUSTON")],
            ),
            Select(
                name="job_type",
                options=[("ASBUILT", "ASBUILT"), ("DESIGN", "DESIGN")],
            ),
            Button("Save", action="save"),
        ]

    def action_save(self):
        pass
        #
        # data = self.collect_data()
        #
        # meta = JobMeta(
        #     details=data["details"],
        #     job_type=JobType(data["job_type"]),
        #     task_name=data["task_name"],
        #     company_name=data["company_name"],
        #     region=region_from_str(data["region"]),
        #     address=data["address"],
        #     lat=data["lat"],
        #     long=data["long"],
        #     clli=data["clli"],
        # )
        #
        # job = Job(
        #     id=JobId(data["id"]),
        #     meta=meta,
        #     network=NetworkSpec(),
        # )
        #
        # self.dismiss(job)
        self.app.pop_screen()
