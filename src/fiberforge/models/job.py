from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional, Literal, Union

from .common import Serializable
from .ids import DeviceId, JobId, MuxId, SpanId

# ---------------------------------------------------------------------------
# Rust‑style Region Variants
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MWR(Serializable):
    folder: str = "MWR"


@dataclass(frozen=True)
class BSR(Serializable):
    folder: str = "BSR"


@dataclass(frozen=True)
class HOUSTON(Serializable):
    folder: str = "HOUSTON"


JobRegion = Union[MWR, BSR, HOUSTON]

REGION_TYPES = {
    "MWR": MWR,
    "BSR": BSR,
    "HOUSTON": HOUSTON,
}


# ---------------------------------------------------------------------------
# Job Type (simple enum for now)
# ---------------------------------------------------------------------------


class JobType(Enum):
    ASBUILT = "ASBUILT"
    DESIGN = "DESIGN"


# ---------------------------------------------------------------------------
# Job Phase (simple enum for now)
# ---------------------------------------------------------------------------


class JobPhase(Enum):
    CREATED = "CREATED"
    PREPARED = "PREPARED"
    PLANNING = "PLANNING"
    COMPLETED = "COMPLETED"


# ---------------------------------------------------------------------------
# Job Metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JobMeta(Serializable):
    details: str
    job_type: JobType
    task_name: str
    company_name: str
    region: JobRegion
    address: str
    lat: str
    long: str
    clli: str
    revision_number: int = 0
    notes: str = "No Notes"

    # -------------------------
    # Validation
    # -------------------------

    def validate_clli(self) -> list[str]:
        errors: list[str] = []

        # Rust‑style pattern matching
        match self.region:
            case HOUSTON() | MWR():
                if self.job_type == JobType.ASBUILT and not self.clli:
                    errors.append("CLLI is required for HOUSTON/MWR Asbuilts")

        return errors


# ---------------------------------------------------------------------------
# CFAT Specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CfatSpec(Serializable):
    mux_id: MuxId
    distance_to_hub: int
    bandwidth: Literal[1, 10, 100]
    preterm: str
    ext_id: str

    @staticmethod
    def is_needed(meta: JobMeta) -> list[str]:
        match meta.region:
            case HOUSTON() | MWR():
                if meta.job_type == JobType.DESIGN:
                    return ["CFAT is required for MWR/HOUSTON Design jobs"]
        return []


# ---------------------------------------------------------------------------
# Network Specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NetworkSpec(Serializable):
    nodes: Iterable[str] = field(default_factory=tuple)
    segment: Optional[str] = None
    hubs: Iterable[str] = field(default_factory=tuple)
    endsites: Iterable[DeviceId] = field(default_factory=tuple)
    removing: Iterable[DeviceId | SpanId] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Job Aggregate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Job(Serializable):
    id: JobId
    meta: Optional[JobMeta] = None
    network: Optional[NetworkSpec] = None
    cfat: Optional[CfatSpec] = None

    # -------------------------
    # Derived helpers
    # -------------------------

    @property
    def label(self) -> str:
        return f"{self.id} — {self.meta.company_name if self.meta else 'Unnamed Job'}"

    def validate(self) -> list[str]:
        errors: list[str] = []
        errors += self.meta.validate_clli() if self.meta else []
        if not self.cfat:
            errors += CfatSpec.is_needed(self.meta) if self.meta else []
        return errors
