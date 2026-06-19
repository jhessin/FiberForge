import sqlite3
from pathlib import Path
from typing import Optional

from fiberforge.models import Job, JobId


# 3. Typed Database Operations Manager
class Store:

    def __init__(self, db_path: Path) -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(db_path / "data.db")
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self._initialize_db()

    def _initialize_db(self) -> None:
        """This is where we will initialize all of the tables in the database"""
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS jobs (
        #         id TEXT PRIMARY KEY,
        #         updated_date TEXT, -- Stored as ISO string text for fast SQLite indexing
        #         data BLOB
        #     )
        # """)
        #
        # self.cursor.execute(
        #     "CREATE INDEX IF NOT EXISTS idx_config_date ON configs(updated_date)"
        # )

        HERE = Path(__file__).resolve().parent
        schema = HERE / "schema.sql"

        self.conn.executescript(schema.read_text())
        self.conn.commit()

    def load_jobs(self) -> list[JobId]:
        # TODO: This should load all jobs.
        self.cursor.execute("SELECT id FROM Jobs")
        result: list[tuple[str, ...]] = self.cursor.fetchall()
        if result:
            return [JobId(id) for id_tuple in result for id in id_tuple]
        return []

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        self.cursor.execute("SELECT data FROM Jobs WHERE id = ?", (job_id,))
        row: Optional[tuple[bytes]] = self.cursor.fetchone()
        if row is None:
            return None
        return Job.from_binary(row[0])

    # def get_by_id(self, config_id: int) -> Optional[Address]:
    #     self.cursor.execute("SELECT data FROM configs WHERE id = ?", (config_id,))
    #     row: Optional[tuple[bytes]] = self.cursor.fetchone()
    #     if row is None:
    #         return None
    #     return Address.from_binary(row[0])
    #
    # def get_date_range(
    #     self, start_date: datetime, end_date: datetime
    # ) -> List[Serializable]:
    #     """Allows direct querying using Native Python datetime parameters."""
    #     # Query utilizing SQLite's standard alpha-sortable ISO string dates
    #     self.cursor.execute(
    #         "SELECT data FROM configs WHERE updated_date BETWEEN ? AND ?",
    #         (start_date.isoformat(), end_date.isoformat()),
    #     )
    #     rows: List[tuple[bytes]] = self.cursor.fetchall()
    #
    #     return [AppConfig.from_binary(row[0]) for row in rows]

    def save_job(self, job: Job) -> None:
        binary_blob: bytes = job.to_binary()
        self.cursor.execute(
            """
        INSERT OR REPLACE INTO Jobs (id, data) VALUES (?, ?)
        """,
            (job.id.value, binary_blob),
        )
        self.conn.commit()

    # def save_or_update(self, config: Address) -> None:
    #     binary_blob: bytes = config.to_binary()
    #
    #     self.cursor.execute(
    #         """
    #         INSERT OR REPLACE INTO configs (id, updated_date, data)
    #         VALUES (?, ?, ?)
    #     """,
    #         (config.config_id, config.updated_date.isoformat(), binary_blob),
    #     )
    #     self.conn.commit()

    def close(self) -> None:
        self.conn.close()
