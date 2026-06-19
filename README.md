# FiberForge

FiberForge is a domain‑driven fiber‑network modeling toolkit and Textual‑based
TUI application.  It provides a structured way to model fiber runs, spans, cans,
muxes, splices, and job metadata using a clean, immutable, and fully
serializable domain model.

FiberForge is built for technicians, engineers, and planners who need a fast,
local, terminal‑native workspace for understanding and manipulating fiber
network data.

---

## Features

- **Domain‑Driven Model**
  - Immutable dataclasses for all fiber‑network entities
  - Unified `Serializable` protocol for clean JSON persistence
  - Strong typing across spans, runs, muxes, cans, and jobs

- **Textual TUI**
  - Fast, keyboard‑driven interface
  - Panels for jobs, runs, spans, and details
  - Rich‑powered rendering

- **Flexible Fiber Modeling**
  - Named spans with multiple measured segments (UG, OL, INSIDE, SLACK, RISER)
  - Fiber runs composed immutably
  - Filters for selecting span types
  - Builders and services for domain logic

- **JSON Repository**
  - Clean, generic persistence layer
  - Automatic serialization/deserialization of all domain objects

---

## Installation

FiberForge uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv run fiberforge
```
