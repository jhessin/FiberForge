# filters.py
from dataclasses import dataclass
from typing import Any, TypeVar

from .span import Span
from .common import Serializable

T = TypeVar("T", bound="Filter")


@dataclass(frozen=True)
class Filter(Serializable):
    """A filter can be used to sort out MeasuredSpan lengths"""

    name: str
    data: tuple[type[Span.MeasuredSpan], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "data": [cls.__name__ for cls in self.data],
        }

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        span_types = tuple(getattr(Span, t) for t in data["data"])
        return cls(
            name=data["name"],
            data=span_types,
        )


BASE_FILTER = Filter(
    "Basic",
    (
        Span.UG,
        Span.OL,
        Span.INSIDE,
    ),
)

SLACK_FILTER = Filter("Slack", (Span.SLACK,))

RISER_FILTER = Filter("Risers", (Span.RISER,))

OL_FILTER = Filter("Total OL", (Span.OL,))

UG_FILTER = Filter(
    "Total UG",
    (
        Span.UG,
        Span.INSIDE,
    ),
)

UG_WITH_RISERS = Filter(
    "UG with Risers",
    (
        Span.UG,
        Span.RISER,
    ),
)
