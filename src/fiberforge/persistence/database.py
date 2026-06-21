import sqlite3
from contextlib import AbstractContextManager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from platformdirs import PlatformDirs

from fiberforge.models import Job, JobId
from fiberforge.models.time_clock import TimeClock, TimeSpan

dirs = PlatformDirs('FiberForge', 'GrillbrickStudios')
data_dir = dirs.user_data_path


# 3. Typed Database Operations Manager
class Database(AbstractContextManager):
    def __init__(self) -> None:
        self.open()
        self._initialize_db()

    def __enter__(self) -> 'Database':
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback,
    ):
        del exc_type, exc_value, traceback
        self.close()

    def open(self):
        self.conn: sqlite3.Connection = sqlite3.connect(data_dir / 'data.db')
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    def _initialize_db(self) -> None:
        """This is where we will initialize all of the tables in the database"""

        HERE = Path(__file__).resolve().parent
        schema = HERE / 'schema.sql'

        self.conn.executescript(schema.read_text())
        self.conn.commit()

    def load_jobs(self) -> list[JobId]:
        self.cursor.execute('SELECT id FROM Jobs')
        result: list[tuple[str, ...]] = self.cursor.fetchall()
        if result:
            return [JobId(id) for id_tuple in result for id in id_tuple]
        return []

    def load_todays_jobs(self) -> list[JobId]:
        self.cursor.execute(
            'SELECT DISTINCT job_id FROM TimeClock WHERE start > ?',
            (datetime.combine(datetime.today(), datetime.min.time()).isoformat(),),
        )
        jobs: list[str] = self.cursor.fetchall()
        return [JobId(j) for j in jobs]

    def load_clock(self, day: date) -> TimeClock:
        spans: list[TimeSpan] = []
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)

        self.cursor.execute(
            'SELECT * FROM TimeClock WHERE start >= ? AND start < ?',
            (start.isoformat(), end.isoformat()),
        )
        for start, end, job_id, _ in self.cursor.fetchall():
            spans.append(
                TimeSpan(
                    start=datetime.fromisoformat(start),
                    end=datetime.fromisoformat(end) if end else None,
                    job_id=JobId(job_id),
                )
            )
        return TimeClock(tuple(spans))

    def save_clock(self, clock: TimeClock) -> None:
        for span in clock.time_spans:
            self.cursor.execute(
                """
            INSERT OR REPLACE INTO TimeClock (start, end, job_id, version)
            VALUES (?, ?, ?, 1)
            """,
                (
                    span.start.isoformat(),
                    span.end.isoformat() if span.end else None,
                    span.job_id.value,
                ),
            )
        self.conn.commit()

    def load_todays_clock(self) -> TimeClock:
        spans: list[TimeSpan] = []
        self.cursor.execute(
            'SELECT * FROM TimeClock WHERE start > ?',
            (
                # datetime.now()
                # .replace(hour=0, minute=0, second=0, microsecond=0)
                # .isoformat(),
                datetime.combine(datetime.today(), datetime.min.time()).isoformat(),
            ),
        )
        for job_id, start, end, _ in self.cursor.fetchall():
            spans.append(
                TimeSpan(
                    start=datetime.fromisoformat(start),
                    end=datetime.fromisoformat(end) if end else None,
                    job_id=JobId(job_id),
                )
            )
        return TimeClock(tuple(spans))

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        self.cursor.execute('SELECT data FROM Jobs WHERE id = ?', job_id)
        row: Optional[tuple[bytes]] = self.cursor.fetchone()
        if row is None:
            return None
        return Job.from_binary(row[0])

    def delete_job(self, job_id: str) -> None:
        self.cursor.execute('DELETE FROM Jobs WHERE id = ?', (job_id,))
        self.conn.commit()

    def save_job(self, job: Job) -> None:
        binary_blob: bytes = job.to_binary()
        self.cursor.execute(
            """
        INSERT OR REPLACE INTO Jobs (id, data) VALUES (?, ?)
        """,
            (job.id.value, binary_blob),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
