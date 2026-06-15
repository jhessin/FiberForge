from abc import ABC
from dataclasses import dataclass
from typing import Literal

from .ids import CanId, MuxId
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
    can: CanId

    @classmethod
    def from_dict(cls, data: dict) -> "Mux":
        model_name = data["model"]["name"]
        count = data["model"]["channel_count"]

        if model_name == "CWDM":
            model = CWDM(count)
        elif model_name == "DWDM":
            model = DWDM(count)
        else:
            raise ValueError(f"Unknown mux model: {model_name}")

        channels = tuple(MuxChannel(c) for c in data["channels"])

        return cls(
            id=MuxId(data["id"]),
            model=model,
            channels=channels,
            address=Address.from_dict(data["address"]),
            can=CanId(data["can"]),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "model": {
                "name": self.model.name,
                "channel_count": self.model.channel_count,
            },
            "channels": [c.value for c in self.channels],
            "address": self.address.to_dict(),
            "can": self.can.value,
        }
