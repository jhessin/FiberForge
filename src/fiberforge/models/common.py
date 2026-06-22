from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional, Type, TypeVar

import dill

from .ids import DeviceId

# Type Aliases
SerializedPayload = dict[str, Any]
T = TypeVar('T', bound='Serializable')


@dataclass(frozen=True)
class GeoTag:
    lat: str
    long: str


@dataclass(frozen=True)
class Serializable(ABC):
    def to_binary(self) -> bytes:
        """Serializes the dataclass fields to a dill binary BLOB."""
        return dill.dumps(self)

    @classmethod
    def from_binary(cls: Type[T], binary_blob: bytes) -> T:
        """Constructs a fresh immutable instance from a binary BLOB."""
        return dill.loads(binary_blob)


@dataclass(frozen=True)
class Address(Serializable):
    value: str


@dataclass(frozen=True)
class FiberDevice(Serializable):
    id: DeviceId
    geo_tag: Optional[GeoTag] = None


class Color(Enum):
    BL = auto()
    OR = auto()
    GR = auto()
    BR = auto()
    SL = auto()
    WH = auto()
    RD = auto()
    BK = auto()
    YL = auto()
    VI = auto()
    RS = auto()
    AQ = auto()
