from typing import Dict, List

from fiberforge.models import FiberId, FiberRun, NamedSpan, SpanId
from fiberforge.models.common import FiberDevice


class LookupService:
    def __init__(
        self,
        spans: Dict[SpanId, NamedSpan],
        cans: Dict[FiberId, FiberDevice],
        runs: List[FiberRun],
    ):
        self.spans = spans
        self.cans = cans
        self.runs = runs

    # -------------------------
    # Span lookups
    # -------------------------

    def span(self, sid: SpanId) -> NamedSpan:
        return self.spans[sid]

    def spans_for_device(self, cid: FiberId) -> list[FiberDevice]:
        """TODO: return the spans for a given fiber device"""
        return []

    # -------------------------
    # Can lookups
    # -------------------------

    def device(self, cid: FiberId) -> FiberDevice:
        return self.cans[cid]

    # -------------------------
    # Run lookups
    # -------------------------

    def runs_containing_span(self, sid: SpanId):
        return [run for run in self.runs if any(s.id == sid for s in run.spans)]
