from fiberforge.models import FiberRun, Filter, Span
from models import MeasuredSpan


class LengthService:

    @staticmethod
    def total(run: FiberRun) -> int:
        return sum(sum(seg.lengths) for span in run.spans for seg in span.spans)

    @staticmethod
    def by_filter(run: FiberRun, flt: Filter) -> int:
        """Sum lengths of all measured spans matching the filter."""
        return sum(
            sum(seg.lengths)
            for span in run.spans
            for seg in span.spans
            if isinstance(seg, flt.data)
        )

    @staticmethod
    def by_type(run: FiberRun, t: type[MeasuredSpan]) -> int:
        """Sum lengths of all measured spans of a specific type."""
        return sum(
            sum(seg.lengths)
            for span in run.spans
            for seg in span.spans
            if isinstance(seg, t)
        )

    @staticmethod
    def slack(run: FiberRun) -> int:
        return LengthService.by_type(run, Span.SLACK)

    @staticmethod
    def riser(run: FiberRun) -> int:
        return LengthService.by_type(run, Span.RISER)
