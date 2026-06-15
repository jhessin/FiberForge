# fiberforge/persistence/json_repo.py

from __future__ import annotations
from pathlib import Path
from typing import Type, TypeVar, Iterable, Any
import orjson

from fiberforge.models.common import Serializable
from fiberforge.models.ids import JobId, SpanId, CanId, MuxId
from fiberforge.models.job import Job
from fiberforge.models.span import NamedSpan
from fiberforge.models.can import Can
from fiberforge.models.mux import Mux
from fiberforge.models.fiber_run import FiberRun

T = TypeVar("T", bound=Serializable)


class JsonRepository:
    """
    Crash‑proof JSON repository using the Serializable protocol.

    - Missing files → return empty collections
    - Missing directories → auto‑create
    - Corrupted JSON → fallback to empty
    - Uses orjson for speed
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Low‑level helpers
    # ------------------------------------------------------------

    def _safe_load(self, filename: str) -> Any:
        path = self.data_dir / filename

        if not path.exists():
            return None

        try:
            return orjson.loads(path.read_bytes())
        except Exception:
            # Optional: log a warning
            return None

    def _safe_save(self, filename: str, data: Any) -> None:
        path = self.data_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    # ------------------------------------------------------------
    # Generic loaders
    # ------------------------------------------------------------

    def load_list(self, filename: str, cls: Type[T]) -> list[T]:
        raw = self._safe_load(filename)
        if not raw:
            return []
        return [cls.from_dict(item) for item in raw]

    def save_list(self, filename: str, items: Iterable[T]) -> None:
        data = [item.to_dict() for item in items]
        self._safe_save(filename, data)

    def load_dict(self, filename: str, cls: Type[T], key_type) -> dict[Any, T]:
        raw = self._safe_load(filename)
        if not raw:
            return {}
        return {key_type(k): cls.from_dict(v) for k, v in raw.items()}

    def save_dict(self, filename: str, items: dict[Any, T]) -> None:
        data = {str(k): v.to_dict() for k, v in items.items()}
        self._safe_save(filename, data)

    # ------------------------------------------------------------
    # Domain‑specific loaders
    # ------------------------------------------------------------

    def load_jobs(self) -> dict[JobId, Job]:
        return self.load_dict("jobs.json", Job, JobId)

    def save_jobs(self, jobs: dict[JobId, Job]) -> None:
        self.save_dict("jobs.json", jobs)

    def load_spans(self) -> dict[SpanId, NamedSpan]:
        return self.load_dict("spans.json", NamedSpan, SpanId)

    def save_spans(self, spans: dict[SpanId, NamedSpan]) -> None:
        self.save_dict("spans.json", spans)

    def load_cans(self) -> dict[CanId, Can]:
        return self.load_dict("cans.json", Can, CanId)

    def save_cans(self, cans: dict[CanId, Can]) -> None:
        self.save_dict("cans.json", cans)

    def load_muxes(self) -> dict[MuxId, Mux]:
        return self.load_dict("muxes.json", Mux, MuxId)

    def save_muxes(self, muxes: dict[MuxId, Mux]) -> None:
        self.save_dict("muxes.json", muxes)

    def load_runs(self) -> list[FiberRun]:
        return self.load_list("runs.json", FiberRun)

    def save_runs(self, runs: list[FiberRun]) -> None:
        self.save_list("runs.json", runs)
