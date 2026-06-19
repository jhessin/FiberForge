from datetime import datetime
from abc import ABC
from dataclasses import dataclass, asdict
from typing import Any, Type, TypeVar, cast
from enum import Enum, auto

import msgpack

from .ids import DeviceId

# Type Aliases
SerializedPayload = dict[str, Any]
T = TypeVar("T", bound="Serializable")


# 1. Custom MessagePack Hooks for Datetime Conversion
def encode_datetime_hook(obj: Any) -> Any:
    """Tells MessagePack how to transform a datetime into a type it supports."""
    if isinstance(obj, datetime):
        # Store everything cleanly in ISO format string
        return {"__datetime__": True, "as_iso": obj.isoformat()}
    return obj


def decode_datetime_hook(obj: dict[Any, Any]) -> Any:
    """Tells MessagePack how to transform its custom dict back into a datetime."""
    if "__datetime__" in obj:
        # Convert the string back into a true Python datetime object
        return datetime.fromisoformat(obj["as_iso"])
    return obj


@dataclass(frozen=True)
class Serializable(ABC):

    def to_binary(self) -> bytes:
        """Serializes the dataclass fields to a MessagePack binary BLOB."""
        data_dict: SerializedPayload = asdict(self)
        # Use default= hook to catch custom types like datetime
        return msgpack.packb(data_dict, default=encode_datetime_hook)

    @classmethod
    def from_binary(cls: Type[T], binary_blob: bytes) -> T:
        """Constructs a fresh immutable instance from a binary BLOB."""
        # Use object_hook to intercept fields and convert them back into datetime
        unpacked_data = cast(
            SerializedPayload,
            msgpack.unpackb(binary_blob, object_hook=decode_datetime_hook),
        )
        return cls(**unpacked_data)


@dataclass(frozen=True)
class Address(Serializable):
    value: str


@dataclass(frozen=True)
class FiberDevice(Serializable):
    id: DeviceId


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
