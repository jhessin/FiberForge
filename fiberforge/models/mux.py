from abc import ABC
from dataclasses import dataclass
from typing import Literal

from .ids import DeviceId, MuxId
from .common import Address, Serializable


@dataclass(frozen=True)
class MuxChannel:
    value: int | Literal["COM"] = "COM"


@dataclass(frozen=True)
class MuxModel(ABC):
    name: str
    channel_count: int


@dataclass(frozen=True)
class CWDM(MuxModel):
    def __init__(self, channel_count: int):
        super().__init__("CWDM", channel_count)


@dataclass(frozen=True)
class DWDM(MuxModel):
    def __init__(self, channel_count: int):
        super().__init__("DWDM", channel_count)


@dataclass(frozen=True)
class Mux(Serializable):
    id: MuxId
    model: MuxModel
    channels: tuple[MuxChannel, ...]
    address: Address
    can: DeviceId
