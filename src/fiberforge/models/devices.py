from dataclasses import dataclass
from typing import Optional

from .common import FiberDevice, Serializable, Color
from .ids import DeviceId, FiberId, SpanId, PortId

# ---------- Splice Model ----------


@dataclass(frozen=True)
class FiberColor(Serializable):
    tracer: bool
    buffer: Color
    color: Color


@dataclass(frozen=True)
class FiberRef(Serializable):
    """Representing a single fibere inside a sheath"""

    span_id: SpanId
    fiber: int  # 1-based index
    color: Optional[FiberColor] = None

    @property
    def id(self) -> FiberId:
        return FiberId(f"{self.span_id.value} FIBER {self.fiber}")

    def __str__(self) -> str:
        if self.color:
            return f"{self.span_id.value} FIBER {self.fiber} {"T-" if self.color.tracer else ""}{self.color.buffer}{self.color.color}"
        return f"{self.span_id.value} FIBER {self.fiber}"


@dataclass(frozen=True)
class PortRef(Serializable):
    """Represents a port on a splice panel"""

    panel_id: DeviceId
    port: int

    @property
    def id(self) -> PortId:
        return PortId(f"{self.panel_id} PORT {self.port}")

    def __str__(self) -> str:
        return self.id.value


@dataclass(frozen=True)
class Splice(Serializable):
    """Representing a splice between two particular fibers"""

    a: FiberRef
    b: FiberRef


@dataclass(frozen=True)
class PortSplice(Serializable):
    """Represents a splice into a TermPanel"""

    a: FiberRef
    b: PortRef


@dataclass(frozen=True)
class SpliceCan(FiberDevice):
    spans: tuple[SpanId, ...]
    splices: tuple[Splice, ...] = ()


@dataclass(frozen=True)
class TermPanel(FiberDevice):
    spans: tuple[SpanId, ...]
    splices: tuple[PortSplice, ...] = ()


@dataclass(frozen=True)
class Hub(FiberDevice):
    spans: tuple[SpanId, ...]
    splices: tuple[PortSplice, ...]
