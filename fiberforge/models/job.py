from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Iterable, Optional, Literal, Union

from .common import Serializable
from .time_clock import TimeClock, TimeSpan
from .ids import JobId, MuxId

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


def region_to_str(region: JobRegion) -> str:
    return region.folder


def region_from_str(name: str) -> JobRegion:
    return REGION_TYPES[name]()


# ---------------------------------------------------------------------------
# Job Type (simple enum for now)
# ---------------------------------------------------------------------------


class JobType(Enum):
    ASBUILT = "ASBUILT"
    DESIGN = "DESIGN"


# ---------------------------------------------------------------------------
# Job Metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JobMeta(Serializable):
    job_name: str
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
    # Serialization
    # -------------------------

    def to_dict(self) -> dict:
        return {
            "job_name": self.job_name,
            "details": self.details,
            "job_type": self.job_type.value,
            "task_name": self.task_name,
            "company_name": self.company_name,
            "region": region_to_str(self.region),
            "address": self.address,
            "lat": self.lat,
            "long": self.long,
            "clli": self.clli,
            "revision_number": self.revision_number,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JobMeta":
        return cls(
            job_name=data["job_name"],
            details=data["details"],
            job_type=JobType(data["job_type"]),
            task_name=data["task_name"],
            company_name=data["company_name"],
            region=region_from_str(data["region"]),
            address=data["address"],
            lat=data["lat"],
            long=data["long"],
            clli=data["clli"],
            revision_number=data.get("revision_number", 0),
            notes=data.get("notes", "No Notes"),
        )

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


@dataclass
class CfatSpec(Serializable):
    mux_id: MuxId
    distance_to_hub: int
    bandwidth: Literal[1, 10, 100]
    preterm: str
    ext_id: str

    def to_dict(self) -> dict:
        return {
            "mux_id": self.mux_id.value,
            "distance_to_hub": self.distance_to_hub,
            "bandwidth": self.bandwidth,
            "preterm": self.preterm,
            "ext_id": self.ext_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CfatSpec":
        return cls(
            mux_id=MuxId(data["mux_id"]),
            distance_to_hub=data["distance_to_hub"],
            bandwidth=data["bandwidth"],
            preterm=data["preterm"],
            ext_id=data["ext_id"],
        )

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


@dataclass
class NetworkSpec(Serializable):
    nodes: Iterable[str] | str = field(default_factory=tuple)
    segment: Optional[str] = None
    hubs: Iterable[str] | str = field(default_factory=tuple)
    endsites: Iterable[str] | str = field(default_factory=tuple)
    cans_involved: Iterable[str] | str = field(default_factory=tuple)
    runs_only: bool = False
    removing: Iterable[str] | str = field(default_factory=tuple)
    lunch_time: Optional[timedelta] = None

    def to_dict(self) -> dict:
        return {
            "nodes": list(self.nodes),
            "segment": self.segment,
            "hubs": list(self.hubs),
            "endsites": list(self.endsites),
            "cans_involved": list(self.cans_involved),
            "runs_only": self.runs_only,
            "removing": list(self.removing),
            "lunch_time": self.lunch_time.total_seconds() if self.lunch_time else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkSpec":
        ns = NetworkSpec(
            nodes=data["nodes"],
            segment=data.get("segment"),
            hubs=data["hubs"],
            endsites=data["endsites"],
            cans_involved=data["cans_involved"],
            runs_only=data.get("runs_only", False),
            removing=data.get("removing", []),
            lunch_time=(
                timedelta(seconds=data["lunch_time"])
                if data.get("lunch_time") is not None
                else None
            ),
        )
        ns.normalize()
        return ns

    def normalize(self) -> None:
        def to_tuple(v):
            if isinstance(v, str):
                return (v,)
            return tuple(v)

        self.nodes = to_tuple(self.nodes)
        self.hubs = to_tuple(self.hubs)
        self.endsites = to_tuple(self.endsites)
        self.cans_involved = to_tuple(self.cans_involved)
        self.removing = to_tuple(self.removing)


# ---------------------------------------------------------------------------
# Job Aggregate
# ---------------------------------------------------------------------------


@dataclass
class Job(Serializable):
    id: JobId
    meta: JobMeta
    network: NetworkSpec
    cfat: Optional[CfatSpec] = None
    timeclock: TimeClock = field(default_factory=TimeClock)

    # -------------------------
    # TimeClock Operations
    # -------------------------

    def clock_in(self, when: Optional[datetime] = None) -> None:
        when = when or datetime.now()
        new_span = TimeSpan(start=when, end=None)
        self.timeclock = self.timeclock + new_span

    def clock_out(self, when: Optional[datetime] = None) -> None:
        when = when or datetime.now()
        last = self.timeclock.time_spans[-1]
        if last.is_completed:
            raise ValueError("Cannot clock out; no active time span")
        updated = last.update_end(when)
        spans = self.timeclock.time_spans[:-1] + (updated,)
        self.timeclock = TimeClock(spans)

    # -------------------------
    # Derived helpers
    # -------------------------

    @property
    def total_time(self) -> timedelta:
        return self.timeclock.total_time

    @property
    def active_span(self) -> Optional[TimeSpan]:
        if not self.timeclock.time_spans:
            return None
        last = self.timeclock.time_spans[-1]
        return None if last.is_completed else last

    @property
    def label(self) -> str:
        return f"{self.id} — {self.meta.job_name or 'Unnamed Job'}"

    @property
    def summary(self) -> str:
        return f"{self.id} | {self.meta.job_type.value} | {self.meta.region.folder}"

    def validate(self) -> list[str]:
        errors: list[str] = []
        errors += self.meta.validate_clli()
        if not self.cfat:
            errors += CfatSpec.is_needed(self.meta)
        return errors

    # -------------------------
    # Serialization
    # -------------------------

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "meta": self.meta.to_dict(),
            "network": self.network.to_dict(),
            "cfat": self.cfat.to_dict() if self.cfat else None,
            "timeclock": self.timeclock.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        return cls(
            id=JobId(data["id"]),
            meta=JobMeta.from_dict(data["meta"]),
            network=NetworkSpec.from_dict(data["network"]),
            cfat=(
                CfatSpec.from_dict(data["cfat"])
                if data.get("cfat") is not None
                else None
            ),
            timeclock=TimeClock.from_dict(data["timeclock"]),
        )
