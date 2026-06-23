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


class Database(AbstractContextManager):
    class Jobs:
        def __init__(self, db: 'Database') -> None:
            self.db: Database = db

        def load(self) -> tuple[JobId, ...]:
            self.db.cursor.execute('SELECT id FROM Jobs')
            result: list[str] = self.db.cursor.fetchall()
            if result:
                final_answer = [JobId(id) for id_tuple in result for id in id_tuple]
                return tuple(final_answer)
            return ()

        def save(self, job: Job) -> None:
            binary_blob: bytes = job.to_binary()
            self.db.cursor.execute(
                """
            INSERT OR REPLACE INTO Jobs (id, data) VALUES (?, ?)
            """,
                (job.id.value, binary_blob),
            )
            self.db.conn.commit()

        def today(self) -> list[JobId]:
            self.db.cursor.execute(
                'SELECT DISTINCT job_id FROM TimeClock WHERE start > ?',
                (datetime.combine(datetime.today(), datetime.min.time()).isoformat(),),
            )
            jobs: list[str] = self.db.cursor.fetchall()
            return [JobId(j) for j in jobs]

        def active(self) -> Optional[Job]:
            self.db.cursor.execute("""
            SELECT job_id FROM TimeClock
            WHERE end IS NULL
            """)
            job_id: Optional[str] = self.db.cursor.fetchone()
            if job_id:
                return self.by_id(job_id)
            return None

        def by_id(self, job_id: str) -> Optional[Job]:
            self.db.cursor.execute('SELECT data FROM Jobs WHERE id = ?', (job_id,))
            row: Optional[tuple[bytes]] = self.db.cursor.fetchone()
            if row is None:
                return None
            return Job.from_binary(row[0])

        def delete(self, job_id: str) -> None:
            self.db.cursor.execute('DELETE FROM Jobs WHERE id = ?', (job_id,))
            self.db.cursor.execute('DELETE FROM TimeClock WHERE job_id = ?', (job_id,))
            self.db.cursor.execute('DELETE FROM Runs WHERE job_id = ?', (job_id,))
            self.db.conn.commit()

    class Clock:
        def __init__(self, db: 'Database') -> None:
            self.db: Database = db

        def load(self, day: date) -> TimeClock:
            spans: list[TimeSpan] = []
            start = datetime.combine(day, datetime.min.time())
            end = start + timedelta(days=1)

            self.db.cursor.execute(
                'SELECT * FROM TimeClock WHERE start >= ? AND start < ?',
                (start.isoformat(), end.isoformat()),
            )
            for start, end, job_id, _ in self.db.cursor.fetchall():
                spans.append(
                    TimeSpan(
                        start=datetime.fromisoformat(start),
                        end=datetime.fromisoformat(end) if end else None,
                        job_id=JobId(job_id),
                    )
                )
            return TimeClock(tuple(spans))

        def save(self, clock: TimeClock) -> None:
            for span in clock.time_spans:
                self.db.cursor.execute(
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
            self.db.conn.commit()

        def today(self) -> TimeClock:
            spans: list[TimeSpan] = []
            self.db.cursor.execute(
                'SELECT * FROM TimeClock WHERE start > ?',
                (
                    # datetime.now()
                    # .replace(hour=0, minute=0, second=0, microsecond=0)
                    # .isoformat(),
                    datetime.combine(datetime.today(), datetime.min.time()).isoformat(),
                ),
            )
            for job_id, start, end, _ in self.db.cursor.fetchall():
                spans.append(
                    TimeSpan(
                        start=datetime.fromisoformat(start),
                        end=datetime.fromisoformat(end) if end else None,
                        job_id=JobId(job_id),
                    )
                )
            return TimeClock(tuple(spans))

    class Runs:
        def __init__(self, db: 'Database') -> None:
            self.db: Database = db

    def __init__(self) -> None:
        self.jobs: Database.Jobs = Database.Jobs(self)
        self.clock: Database.Clock = Database.Clock(self)
        self.runs: Database.Runs = Database.Runs(self)

        self.__enter__()
        self._initialize_db()
        self.__exit__()

    def __enter__(self) -> 'Database':
        data_dir.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(data_dir / 'data.db')
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        return self

    def __exit__(self, *args, **kwargs):
        del args, kwargs
        self.conn.close()

    def _initialize_db(self) -> None:
        """This is where we will initialize all of the tables in the database"""

        HERE = Path(__file__).resolve().parent
        schema = HERE / 'schema.sql'

        self.conn.executescript(schema.read_text())
        self.conn.commit()
