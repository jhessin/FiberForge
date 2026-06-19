# ids.py

from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class JobId:
    value: str


@dataclass(frozen=True)
class SpanId:
    value: str


@dataclass(frozen=True)
class MuxId:
    value: str


@dataclass(frozen=True)
class DeviceId:
    value: str

    class DeviceType(Enum):
        SPLICE_CAN = auto()
        HUB = auto()
        NODE = auto()
        TERM_PANEL = auto()

    deviceType: DeviceType


@dataclass(frozen=True)
class FiberId:
    value: str


@dataclass(frozen=True)
class PortId:
    value: str
