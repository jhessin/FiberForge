# filters.py
from dataclasses import dataclass
from typing import TypeVar

from .span import Span, MeasuredSpan
from .common import Serializable

T = TypeVar("T", bound="Filter")


@dataclass(frozen=True)
class Filter(Serializable):
    """A filter can be used to sort out MeasuredSpan lengths"""

    name: str
    data: tuple[type[MeasuredSpan], ...]


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
