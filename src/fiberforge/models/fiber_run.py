from dataclasses import dataclass, field
from typing import Iterable, overload

from .common import Serializable

from .span import NamedSpan, MeasuredSpan, Span
from .filters import Filter
from .ids import JobId


@dataclass(frozen=True)
class FiberRun(Serializable):
    """A fiber run is an ordered sequence of NamedSpans belonging to a Job."""

    job_id: JobId
    id: int  # An integer representing the order the run should be listed for the job
    spans: tuple[NamedSpan, ...] = field(default_factory=tuple)

    # ---------- core queries ----------

    def total_length(self) -> int:
        return sum(sum(seg.lengths) for span in self.spans for seg in span.spans)

    def length_for_filter(self, flt: Filter) -> int:
        return sum(
            sum(seg.lengths)
            for span in self.spans
            for seg in span.spans
            if isinstance(seg, flt.data)
        )

    def slack_length(self) -> int:
        return sum(
            sum(seg.lengths)
            for span in self.spans
            for seg in span.spans
            if isinstance(seg, Span.SLACK)
        )

    def riser_length(self) -> int:
        return sum(
            sum(seg.lengths)
            for span in self.spans
            for seg in span.spans
            if isinstance(seg, Span.RISER)
        )

    # ---------- transformation (immutably) ----------

    @overload
    def __add__(self, other: NamedSpan) -> "FiberRun": ...

    @overload
    def __add__(self, other: Iterable[MeasuredSpan]) -> "FiberRun": ...

    @overload
    def __add__(self, other: Iterable[NamedSpan]) -> "FiberRun": ...

    def __add__(self, other):
        # Case 1: A single NamedSpan
        if isinstance(other, NamedSpan):
            return FiberRun(
                id=self.id,
                job_id=self.job_id,
                spans=(*self.spans, other),
            )

        # Case 2: Iterable of NamedSpan
        if isinstance(other, Iterable) and all(isinstance(v, NamedSpan) for v in other):
            return FiberRun(
                id=self.id,
                job_id=self.job_id,
                spans=(*self.spans, *other),
            )

        # Case 3: Iterable of MeasuredSpan → append to last NamedSpan
        if isinstance(other, Iterable) and all(
            isinstance(v, MeasuredSpan) for v in other
        ):
            if not self.spans:
                raise ValueError("Cannot append measured spans to an empty FiberRun")

            *prefix, last = self.spans
            new_last = last + other

            return FiberRun(
                id=self.id,
                job_id=self.job_id,
                spans=(*prefix, new_last),
            )

        raise TypeError(f"Unsupported operand type for +: {type(other)}")
