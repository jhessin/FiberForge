from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional

from .common import Serializable
from .ids import DeviceId, JobId, MuxId, SpanId

# ---------------------------------------------------------------------------
# Rust‑style Region Variants
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JobRegion(Serializable):
    @dataclass(frozen=True)
    class MWR(Serializable):
        folder: str = ''

    @dataclass(frozen=True)
    class BSR(Serializable):
        folder: str = ''

    @dataclass(frozen=True)
    class HOUSTON(Serializable):
        folder: str = 'HOUSTON'

    type Type = MWR | BSR | HOUSTON

    @classmethod
    def is_type(cls, value):
        return isinstance(value, (cls.MWR, cls.BSR, cls.HOUSTON))


# ---------------------------------------------------------------------------
# Job Type (simple enum for now)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JobType(Serializable):
    @dataclass(frozen=True)
    class ASBUILT:
        pass

    @dataclass(frozen=True)
    class DESIGN:
        revision_number: int = 0

    type Type = ASBUILT | DESIGN

    @classmethod
    def is_type(cls, value):
        return isinstance(value, (cls.ASBUILT, cls.DESIGN))


# ---------------------------------------------------------------------------
# Job Phase (simple enum for now)
# ---------------------------------------------------------------------------


class JobPhase(Enum):
    CREATED = 'CREATED'
    PREPARED = 'PREPARED'
    PLANNING = 'PLANNING'
    COMPLETED = 'COMPLETED'


# ---------------------------------------------------------------------------
# Job Metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JobMeta(Serializable):
    job_type: JobType.Type | None = None
    region: JobRegion.Type | None = None
    task_name: str = ''
    company_name: str = ''
    address: str = ''
    lat: str = ''
    long: str = ''
    clli: str = ''
    notes: str = 'No Notes'

    # -------------------------
    # Validation
    # -------------------------

    def validate_clli(self) -> list[str]:
        errors: list[str] = []

        # Rust‑style pattern matching
        match self.region:
            case JobRegion.HOUSTON | JobRegion.MWR:
                if self.job_type == JobType.ASBUILT and not self.clli:
                    errors.append('CLLI is required for HOUSTON/MWR Asbuilts')

        return errors


# ---------------------------------------------------------------------------
# CFAT Specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CfatSpec(Serializable):
    mux_id: MuxId = MuxId('')
    distance_to_hub: int = 0
    bandwidth: Literal[1, 10, 100] = 1
    preterm: str = ''
    ext_id: str = ''

    @staticmethod
    def is_needed(meta: JobMeta) -> list[str]:
        match meta.region:
            case JobRegion.HOUSTON | JobRegion.MWR:
                if meta.job_type == JobType.DESIGN:
                    return ['CFAT is required for MWR/HOUSTON Design jobs']
        return []


# ---------------------------------------------------------------------------
# Network Specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NetworkSpec(Serializable):
    nodes: tuple[str, ...] = field(default_factory=tuple)
    segment: Optional[str] = None
    hubs: tuple[str, ...] = field(default_factory=tuple)
    endsites: tuple[DeviceId, ...] = field(default_factory=tuple)
    removing: tuple[DeviceId | SpanId, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Job Aggregate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Job(Serializable):
    id: JobId
    nickname: Optional[str] = None
    meta: Optional[JobMeta] = None
    network: Optional[NetworkSpec] = None
    cfat: Optional[CfatSpec] = None

    @property
    def label(self) -> str:
        return self.nickname if self.nickname else self.id.value

    @property
    def phase(self) -> JobPhase:
        if self.meta is not None:
            if self.cfat is not None or not CfatSpec.is_needed(self.meta):
                if self.network is not None:
                    return JobPhase.COMPLETED
                return JobPhase.PLANNING
            return JobPhase.PREPARED
        return JobPhase.CREATED
