from typing import Dict, List
from fiberforge.models import SpanId, CanId, NamedSpan, Can, FiberRun


class LookupService:
    def __init__(
        self,
        spans: Dict[SpanId, NamedSpan],
        cans: Dict[CanId, Can],
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

    def spans_for_can(self, cid: CanId):
        return [self.spans[s] for s in self.cans[cid].spans]

    # -------------------------
    # Can lookups
    # -------------------------

    def can(self, cid: CanId) -> Can:
        return self.cans[cid]

    # -------------------------
    # Run lookups
    # -------------------------

    def runs_containing_span(self, sid: SpanId):
        return [run for run in self.runs if any(s.id == sid for s in run.spans)]
