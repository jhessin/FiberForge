CREATE TABLE IF NOT EXISTS "TimeClock" (
  "job_id" TEXT NOT NULL,
  "start" TEXT NOT NULL PRIMARY KEY,
  "end" TEXT NULL
);

CREATE TABLE IF NOT EXISTS "Jobs" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "data" BLOB NOT NULL,
  FOREIGN KEY ("id") REFERENCES "TimeClock"("job_id"),
  FOREIGN KEY ("id") REFERENCES "Runs"("job_id")
);

CREATE TABLE IF NOT EXISTS "Span" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "start_can" TEXT NOT NULL,
  "end_can" TEXT NOT NULL,
  "data" BLOB NOT NULL,
  FOREIGN KEY ("id") REFERENCES "Runs"("spans")
);

CREATE TABLE IF NOT EXISTS "Devices" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "device_type" TEXT NOT NULL,
  "data" BLOB NOT NULL,
  FOREIGN KEY ("id") REFERENCES "Span"("start_can"),
  FOREIGN KEY ("id") REFERENCES "Span"("end_can")
);

CREATE TABLE IF NOT EXISTS "Runs" (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "spans" TEXT NOT NULL,
  "job_id" TEXT NOT NULL,
  CONSTRAINT "uq_Runs_id_job_id" UNIQUE ("id", "job_id")
);
