-- Migration: 2026-01-04
-- Purpose: Remove obsolete table "Main Contract IP_Old" and add foreign-key constraints
-- to "Main Contract IP Item" (MC IP Type, Main Contract BQ, Main Contract VO, Document Manager).
-- IMPORTANT: Backup your database before running this script.

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- Drop obsolete table if it exists
DROP TABLE IF EXISTS "Main Contract IP_Old";

-- Create new table with desired constraints (use temp name)
CREATE TABLE IF NOT EXISTS "Main Contract IP Item_new" (
    "IP" INTEGER,
    "Item" INTEGER,
    "Type" TEXT REFERENCES "MC IP Type" (Type) ON DELETE CASCADE ON UPDATE CASCADE,
    "BQ Ref" TEXT REFERENCES "Main Contract BQ" ("BQ ID") ON DELETE CASCADE ON UPDATE CASCADE,
    "VO Ref" TEXT REFERENCES "Main Contract VO" ("VO ref") ON DELETE CASCADE ON UPDATE CASCADE,
    "DOC Ref" TEXT REFERENCES "Document Manager" (File) ON DELETE CASCADE ON UPDATE CASCADE,
    "Description" TEXT,
    "Applied Amount" REAL,
    "Certified Amount" REAL,
    "Paid Amount" REAL,
    "Remark" TEXT,
    PRIMARY KEY ("IP", "Item"),
    FOREIGN KEY ("IP") REFERENCES "Main Contract IP Application" ("IP") ON DELETE CASCADE
);

-- Copy data (map columns by name; if some columns missing, adjust accordingly)
INSERT INTO "Main Contract IP Item_new" ("IP","Item","Type","BQ Ref","VO Ref","DOC Ref","Description","Applied Amount","Certified Amount","Paid Amount","Remark")
SELECT "IP","Item","Type","BQ Ref","VO Ref","DOC Ref","Description","Applied Amount","Certified Amount","Paid Amount","Remark"
FROM "Main Contract IP Item";

-- Replace old table
DROP TABLE IF EXISTS "Main Contract IP Item";
ALTER TABLE "Main Contract IP Item_new" RENAME TO "Main Contract IP Item";

COMMIT;
PRAGMA foreign_keys = ON;

-- Notes:
-- 1) The migration assumes the existing columns match. If your existing table has different names/columns, adjust the INSERT SELECT mapping.
-- 2) Test this on a copy of the DB first. If you need me to adapt the script to preserve additional metadata, say which columns to map.
