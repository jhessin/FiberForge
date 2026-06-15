# spans.py
from dataclasses import dataclass
from abc import ABC
from typing import overload, Self, Iterable, Any

from .ids import CanId, SpanId
from .common import Serializable


class Span:

    @dataclass(frozen=True)
    class MeasuredSpan(Serializable, ABC):
        lengths: tuple[int, ...]
        new: bool = False

        def to_dict(self) -> dict[str, Any]:
            return {
                "lengths": self.lengths,
                "new": self.new,
            }

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "Span.MeasuredSpan":
            return cls(lengths=data["lengths"], new=data["new"])

        @overload
        def __add__(self, other: int) -> Self: ...
        @overload
        def __add__(self, other: Iterable[int]) -> Self: ...
        @overload
        def __add__(self, other: "Span.MeasuredSpan") -> Self: ...

        def with_lengths(self, new_lengths: Iterable[int]) -> "Span.MeasuredSpan":
            return self.__class__(
                lengths=tuple(new_lengths),
                new=self.new,
            )

        def __add__(self, other):
            # Case 1: add a single length
            if isinstance(other, int):
                return self.with_lengths((*self.lengths, other))

            # Case 2: add multiple lengths
            if isinstance(other, Iterable) and all(isinstance(v, int) for v in other):
                return self.with_lengths((*self.lengths, *other))

            # Case 3: add another MeasuredSpan
            if isinstance(other, Span.MeasuredSpan):
                if self.__class__ is not other.__class__:
                    raise TypeError(
                        f"Cannot add {type(self)} and {type(other)} together."
                    )
                return self.with_lengths((*self.lengths, *other.lengths))

            raise TypeError(f"Cannot add {type(other)} to MeasuredSpan")

    @dataclass(frozen=True)
    class UG(MeasuredSpan):
        pass

    @dataclass(frozen=True)
    class OL(MeasuredSpan):
        pass

    @dataclass(frozen=True)
    class INSIDE(MeasuredSpan):
        new: bool = True

    @dataclass(frozen=True)
    class SLACK(MeasuredSpan):
        pass

    @dataclass(frozen=True)
    class RISER(MeasuredSpan):
        pass


@dataclass(frozen=True)
class NamedSpan(Serializable):
    id: SpanId
    size: int
    spans: tuple[Span.MeasuredSpan, ...]
    start_can: CanId
    end_can: CanId

    def __post_init__(self):
        if self.size <= 0:
            raise ValueError("Fiber size must be positive")
        for s in self.spans:
            if not isinstance(s, Span.MeasuredSpan):
                raise TypeError("All spans must be MeasuredSpan instances")

    @overload
    def __add__(self, other: int) -> "NamedSpan": ...
    @overload
    def __add__(self, other: Iterable[int]) -> "NamedSpan": ...
    @overload
    def __add__(self, other: Span.MeasuredSpan) -> "NamedSpan": ...
    @overload
    def __add__(self, other: Iterable[Span.MeasuredSpan]) -> "NamedSpan": ...

    def __add__(self, other):
        spans = list(self.spans)

        # Case 1: add a single length to last segment
        if isinstance(other, int):
            last = spans[-1]
            new_last = last.__class__(lengths=(*last.lengths, other), new=True)
            spans[-1] = new_last

        # Case 2: add a MeasuredSpan
        elif isinstance(other, Span.MeasuredSpan):
            last = spans[-1]
            if last.__class__ is other.__class__:
                spans[-1] = last + other
            else:
                spans.append(other)

        # Case 3: Iterable
        elif isinstance(other, Iterable):
            items = list(other)

            # Iterable[int]
            if all(isinstance(i, int) for i in items):
                last = spans[-1]
                spans[-1] = last + items

            # Iterable[MeasuredSpan]
            elif all(isinstance(i, Span.MeasuredSpan) for i in items):
                spans.extend(items)

            else:
                raise TypeError("Iterable must contain ints or MeasuredSpan objects")

        else:
            raise TypeError(f"Cannot add {type(other)} to NamedSpan")

        return NamedSpan(
            id=self.id,
            size=self.size,
            spans=tuple(spans),
            start_can=self.start_can,
            end_can=self.end_can,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "NamedSpan":
        span_objs = []
        for s in data["spans"]:
            span_type = getattr(Span, s["type"])
            span_objs.append(span_type(tuple(s["lengths"]), new=s.get("new", False)))

        return cls(
            id=SpanId(data["id"]),
            size=data["size"],
            spans=tuple(span_objs),
            start_can=CanId(data["start_can"]),
            end_can=CanId(data["end_can"]),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "size": self.size,
            "spans": [
                {
                    "type": s.__class__.__name__,
                    "lengths": list(s.lengths),
                    "new": s.new,
                }
                for s in self.spans
            ],
            "start_can": self.start_can.value,
            "end_can": self.end_can.value,
        }
