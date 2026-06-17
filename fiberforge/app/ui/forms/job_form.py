# fiberforge/ui/forms/job_form.py

from __future__ import annotations

from textual.screen import ModalScreen
from textual.widgets import Select
from textual.binding import Binding

from fiberforge.models import (
    Job,
    JobId,
    JobMeta,
    JobType,
    region_from_str,
    NetworkSpec,
)
from .base_form import FormScreen, FormField


class JobFormScreen(FormScreen, ModalScreen[Job]):

    BINDINGS = FormScreen.BINDINGS + [
        Binding("s", "save", "Save"),
    ]

    def build_fields(self):
        return [
            FormField("Job ID", name="id", required=True),
            FormField("Job Name", name="job_name", required=True),
            FormField("Details", name="details"),
            FormField("Task Name", name="task_name", required=True),
            FormField("Company", name="company_name", required=True),
            FormField("Address", name="address", required=True),
            FormField("Latitude", name="lat"),
            FormField("Longitude", name="long"),
            FormField("CLLI", name="clli"),
            # Select widgets
            FormField(
                "Region",
                name="region",
                required=True,
                input_widget=Select(
                    options=[("MWR", "MWR"), ("BSR", "BSR"), ("HOUSTON", "HOUSTON")]
                ),
            ),
            FormField(
                "Job Type",
                name="job_type",
                required=True,
                input_widget=Select(
                    options=[("ASBUILT", "ASBUILT"), ("DESIGN", "DESIGN")]
                ),
            ),
        ]

    def action_save(self):

        data = self.collect_data()

        meta = JobMeta(
            details=data["details"],
            job_type=JobType(data["job_type"]),
            task_name=data["task_name"],
            company_name=data["company_name"],
            region=region_from_str(data["region"]),
            address=data["address"],
            lat=data["lat"],
            long=data["long"],
            clli=data["clli"],
        )

        job = Job(
            id=JobId(data["id"]),
            meta=meta,
            network=NetworkSpec(),
        )

        self.dismiss(job)
