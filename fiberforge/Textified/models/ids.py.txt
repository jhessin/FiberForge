# ids.py

from dataclasses import dataclass


@dataclass(frozen=True)
class JobId:
    value: str


@dataclass(frozen=True)
class SpanId:
    value: str


@dataclass(frozen=True)
class CanId:
    value: str


@dataclass(frozen=True)
class MuxId:
    value: str
