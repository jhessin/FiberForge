from dataclasses import dataclass
from typing import Iterable

from fiberforge.models import NamedSpan, FiberRun, JobId


@dataclass(frozen=True)
class RunBuilder:
    job_id: JobId

    def build(self, spans: Iterable[NamedSpan]) -> FiberRun:
        spans = tuple(spans)

        if not spans:
            raise ValueError("A FiberRun must contain at least one NamedSpan")

        # continuity check
        for a, b in zip(spans, spans[1:]):
            if a.end_can != b.start_can:
                raise ValueError(
                    f"Continuity error: {a.id.value} ends at {a.end_can.value} "
                    f"but next span {b.id.value} starts at {b.start_can.value}"
                )

        return FiberRun(
            job_id=self.job_id,
            spans=spans,
        )
