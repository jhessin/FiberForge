# FiberForge Codebase Documentation

## Overview

FiberForge is a domain-driven fiber network modeling toolkit and Textual-based
TUI application. It provides immutable dataclasses for all fiber-network
entities with a unified `Serializable` protocol for clean JSON persistence. The
app targets technicians, engineers, and planners who need a fast, local,
terminal-native workspace for understanding fiber network data.

## Repository Structure

```bash
fiberforge/
├── src/fiberforge/
│   ├── __init__.py          # Package exports (Domain Model + Repo)
│   ├── cli/                  # Command-line interface entry points
│   │   └── main.py           # Main CLI: init, load, etc.
│   ├── domain/               # Domain model (Serializable protocol + dataclasses)
│   │   ├── entities/         # Run/Span/Fiber/CAN/Mux models
│   │   ├── span_segments.py  # Segment types and segment-to-length conversion
│   │   └── builders/         # Builders for creating objects from JSON
│   ├── jobs/                 # Job management (load/create/list/delete)
│   ├── repo.json             # Repository metadata + versioning info
│   └── tests/                # Tests organized by domain object type
├── README.md                 # Project documentation
└── pyproject.toml            # Poetry-based dependencies and scripts
```

## Key Patterns & Architecture

### Domain Model (Immutable Dataclasses)

All entities follow an immutable dataclass pattern with a `Serializable`
protocol for JSON persistence. Each entity has:

- `id`: Unique identifier
- Built-in equality/hash methods
- Clear serialization/deserialization logic in `_from_dict()` and `_to_jsonable()`

### Repository Pattern

The app uses a central `/repo.json` to persist all domain objects. Jobs are the
top-level container with runs nested inside, containing spans as children.

### Builders Service (`fiberforge.domain.builders`)

- Used when deserializing from JSON files
- Centralizes creation logic for complex entities
- Handles validation (e.g., checking length is a `SpanSegment` if present)

## Development Workflow

1. **Run the app:** See current fiber network state in TUI mode or list all
   jobs/runs via CLI commands
2. **Modify domain objects:** Change dataclasses, segment types, builder logic
   as needed
3. **Test changes:** Run tests for affected modules using pytest
4. **Format code:** `ruff check` + `ruff format`

## Testing Strategy

- Tests are organized by domain object type under `tests/objects/` and `tests/cli/`
- Use pytest fixtures to load jobs from `/repo.json` before running tests

## External Dependencies (per `pyproject.toml`)

### Runtime: textural>=0.58, rich>=13.7, orjson>=3.10, pyperclip>=1.11

The app uses Textual for TUI rendering and Rich for terminal output formatting.
Data is serialized via orjson (faster than `json`), and the clipboard library
handles copy-to-clipboard functionality in rich components.

### Development tools: pytest, ruff, mypy, textual-dev

## How to Start Here

1. Run `poetry install`
2. Use CLI commands like `fiberforge init`, `fiberforge load .../job.json`
3. Browse domain objects with the TUI or filter by type (run/span/can/mux)
