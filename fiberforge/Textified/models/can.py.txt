from dataclasses import dataclass

from .common import Serializable
from .ids import SpanId, CanId

# ---------- Splice Model ----------


@dataclass(frozen=True)
class FiberRef(Serializable):
    span_id: SpanId
    fiber: int  # 1-based index

    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id.value,
            "fiber": self.fiber,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FiberRef":
        return cls(
            span_id=SpanId(data["span_id"]),
            fiber=data["fiber"],
        )


@dataclass(frozen=True)
class Splice(Serializable):
    a: FiberRef
    b: FiberRef

    def to_dict(self) -> dict:
        return {
            "a": self.a.to_dict(),
            "b": self.b.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Splice":
        return cls(
            a=FiberRef.from_dict(data["a"]),
            b=FiberRef.from_dict(data["b"]),
        )


@dataclass(frozen=True)
class Can(Serializable):
    id: CanId
    spans: tuple[SpanId, ...]
    splices: tuple[Splice, ...] = ()

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "spans": [s.value for s in self.spans],
            "splices": [sp.to_dict() for sp in self.splices],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Can":
        return cls(
            id=CanId(data["id"]),
            spans=tuple(SpanId(s) for s in data["spans"]),
            splices=tuple(Splice.from_dict(sp) for sp in data.get("splices", [])),
        )
