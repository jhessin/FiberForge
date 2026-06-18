import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

import msgpack

# Type Aliases
SerializedPayload = Dict[str, Any]
T = TypeVar("T", bound="AppConfig")


# 1. Custom MessagePack Hooks for Datetime Conversion
def encode_datetime_hook(obj: Any) -> Any:
    """Tells MessagePack how to transform a datetime into a type it supports."""
    if isinstance(obj, datetime):
        # Store everything cleanly in ISO format string
        return {"__datetime__": True, "as_iso": obj.isoformat()}
    return obj


def decode_datetime_hook(obj: Dict[Any, Any]) -> Any:
    """Tells MessagePack how to transform its custom dict back into a datetime."""
    if "__datetime__" in obj:
        # Convert the string back into a true Python datetime object
        return datetime.fromisoformat(obj["as_iso"])
    return obj


# 2. Fully Typed Dataclass with native datetime field
@dataclass(frozen=True)
class AppConfig:
    config_id: int
    updated_date: datetime  # Native Python Datetime object
    is_active: bool
    payload: Dict[str, int]

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


# 3. Typed Database Operations Manager
class ConfigurationStore:

    def __init__(self, db_path: str) -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self._initialize_db()

    def _initialize_db(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS configs (
                id INTEGER PRIMARY KEY,
                updated_date TEXT, -- Stored as ISO string text for fast SQLite indexing
                data BLOB
            )
        """)
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_config_date ON configs(updated_date)"
        )
        self.conn.commit()

    def get_by_id(self, config_id: int) -> Optional[AppConfig]:
        self.cursor.execute("SELECT data FROM configs WHERE id = ?", (config_id,))
        row: Optional[tuple[bytes]] = self.cursor.fetchone()
        if row is None:
            return None
        return AppConfig.from_binary(row[0])

    def get_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[AppConfig]:
        """Allows direct querying using Native Python datetime parameters."""
        # Query utilizing SQLite's standard alpha-sortable ISO string dates
        self.cursor.execute(
            "SELECT data FROM configs WHERE updated_date BETWEEN ? AND ?",
            (start_date.isoformat(), end_date.isoformat()),
        )
        rows: List[tuple[bytes]] = self.cursor.fetchall()

        return [AppConfig.from_binary(row[0]) for row in rows]

    def save_or_update(self, config: AppConfig) -> None:
        binary_blob: bytes = config.to_binary()

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO configs (id, updated_date, data) 
            VALUES (?, ?, ?)
        """,
            (config.config_id, config.updated_date.isoformat(), binary_blob),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


# --- Application Workflow Verification ---
if __name__ == "__main__":
    store = ConfigurationStore("typed_datetime_data.db")

    # Save an object with a real datetime instance
    now_utc = datetime.now(timezone.utc)
    config = AppConfig(
        config_id=42,
        updated_date=now_utc,
        is_active=True,
        payload={"max_users": 200},
    )
    store.save_or_update(config)

    # Read back the item
    retrieved: Optional[AppConfig] = store.get_by_id(42)

    if retrieved is not None:
        # Check that it completely preserved the object types
        print(type(retrieved.updated_date))  # Output: <class 'datetime.datetime'>
        print(retrieved.updated_date)  # Output: 2026-06-18 17:08:00...

    store.close()
