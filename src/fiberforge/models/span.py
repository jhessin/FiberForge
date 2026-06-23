# spans.py
from abc import ABC
from dataclasses import dataclass, field
from typing import Iterable, Self, overload

from .common import Serializable
from .ids import DeviceId, SpanId


@dataclass(frozen=True)
class MeasuredSpan(Serializable, ABC):
    lengths: tuple[int, ...]
    new: bool = False

    @overload
    def __add__(self, other: int) -> Self: ...

    @overload
    def __add__(self, other: Iterable[int]) -> Self: ...

    @overload
    def __add__(self, other: 'MeasuredSpan') -> Self: ...

    def with_lengths(self, new_lengths: Iterable[int]) -> 'MeasuredSpan':
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
        if isinstance(other, MeasuredSpan):
            if self.__class__ is not other.__class__:
                raise TypeError(f'Cannot add {type(self)} and {type(other)} together.')
            return self.with_lengths((*self.lengths, *other.lengths))

        raise TypeError(f'Cannot add {type(other)} to MeasuredSpan')


@dataclass(frozen=True)
class Span:
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
    start_can: DeviceId
    end_can: DeviceId
    spans: tuple[MeasuredSpan, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if self.size <= 0:
            raise ValueError('Fiber size must be positive')
        for s in self.spans:
            if not isinstance(s, MeasuredSpan):
                raise TypeError('All spans must be MeasuredSpan instances')

    @overload
    def __add__(self, other: int) -> 'NamedSpan': ...

    @overload
    def __add__(self, other: Iterable[int]) -> 'NamedSpan': ...

    @overload
    def __add__(self, other: MeasuredSpan) -> 'NamedSpan': ...

    @overload
    def __add__(self, other: Iterable[MeasuredSpan]) -> 'NamedSpan': ...

    def __add__(self, other):
        spans = list(self.spans)

        # Case 1: add a single length to last segment
        if isinstance(other, int):
            last: MeasuredSpan = spans[-1]
            new_last = last.__class__(lengths=(*last.lengths, other), new=True)
            spans[-1] = new_last

        # Case 2: add a MeasuredSpan
        elif isinstance(other, MeasuredSpan):
            last: MeasuredSpan = spans[-1]
            if last.__class__ is other.__class__:
                spans[-1] = last + other
            else:
                spans.append(other)

        # Case 3: Iterable
        elif isinstance(other, Iterable):
            # Iterable[int]
            if all(isinstance(i, int) for i in other):
                int_items: list[int] = list(other)
                last = spans[-1]
                spans[-1] = last + int_items

            # Iterable[MeasuredSpan]
            elif all(isinstance(i, MeasuredSpan) for i in other):
                span_items: list[MeasuredSpan] = list(other)
                spans.extend(span_items)

            else:
                raise TypeError('Iterable must contain ints or MeasuredSpan objects')

        else:
            raise TypeError(f'Cannot add {type(other)} to NamedSpan')

        return NamedSpan(
            id=self.id,
            size=self.size,
            spans=tuple(spans),
            start_can=self.start_can,
            end_can=self.end_can,
        )
