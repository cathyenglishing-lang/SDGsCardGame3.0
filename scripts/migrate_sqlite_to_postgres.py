import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SQLITE_PATH = ROOT_DIR / "sql" / "app.db"
TABLES = [
    "users",
    "email_otps",
    "sdg_options",
    "difficulty_options",
    "tbl_sdg_parts",
    "tbl_sdg_sub_topics",
    "tbl_sdg_cards",
    "game_sessions",
    "game_part_records",
]
PRIMARY_KEYS = {
    "users": ["id"],
    "email_otps": ["id"],
    "sdg_options": ["sdg_level"],
    "difficulty_options": ["code"],
    "tbl_sdg_parts": ["part_id"],
    "tbl_sdg_sub_topics": ["sub_topic_id"],
    "tbl_sdg_cards": ["card_id"],
    "game_sessions": ["session_id"],
    "game_part_records": ["id"],
}
IDENTITY_COLUMNS = {
    "users": "id",
    "email_otps": "id",
    "tbl_sdg_parts": "part_id",
    "tbl_sdg_sub_topics": "sub_topic_id",
    "tbl_sdg_cards": "card_id",
    "game_sessions": "session_id",
    "game_part_records": "id",
}


def main():
    parser = argparse.ArgumentParser(description="Migrate local SQLite data to PostgreSQL.")
    parser.add_argument("--sqlite", default=str(SQLITE_PATH), help="Path to source SQLite app.db")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Clear target PostgreSQL tables before importing. Recommended for a new Railway database.",
    )
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL must point to the PostgreSQL database before running this script.")

    sys.path.insert(0, str(ROOT_DIR))
    from backend.main import get_db  # noqa: PLC0415

    sqlite_conn = sqlite3.connect(args.sqlite)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = get_db()
    pg_cur = pg_conn.cursor()

    if args.replace:
        pg_cur.execute(f"TRUNCATE TABLE {', '.join(TABLES)} RESTART IDENTITY CASCADE")

    for table in TABLES:
        rows = [dict(row) for row in sqlite_conn.execute(f"SELECT * FROM {table}").fetchall()]
        if not rows:
            continue

        columns = list(rows[0].keys())
        column_sql = ", ".join(columns)
        placeholders = ", ".join("?" for _ in columns)
        pk_columns = PRIMARY_KEYS[table]
        update_columns = [column for column in columns if column not in pk_columns]
        conflict_sql = f"ON CONFLICT ({', '.join(pk_columns)}) DO NOTHING"
        if update_columns:
            updates = ", ".join(f"{column} = excluded.{column}" for column in update_columns)
            conflict_sql = f"ON CONFLICT ({', '.join(pk_columns)}) DO UPDATE SET {updates}"

        sql = f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders}) {conflict_sql}"
        pg_cur.executemany(sql, [tuple(row[column] for column in columns) for row in rows])
        print(f"Imported {len(rows)} rows into {table}")

    for table, column in IDENTITY_COLUMNS.items():
        pg_cur.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table}', '{column}'),
                COALESCE((SELECT MAX({column}) FROM {table}), 1),
                (SELECT COUNT(*) FROM {table}) > 0
            )
            """
        )

    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    print("SQLite to PostgreSQL migration complete.")


if __name__ == "__main__":
    main()
