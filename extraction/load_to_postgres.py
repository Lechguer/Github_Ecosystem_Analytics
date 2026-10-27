import glob
import json
import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

TABLES = {
    "raw_repos": "repos_*.json",
    "raw_contributors": "contributors_*.json",
    "raw_pull_requests": "pull_requests_*.json",
    "raw_issues": "issues_*.json",
    "raw_commits": "commits_*.json",
    "raw_users": "users_*.json",
}

# Tables rechargees entierement a chaque run (etat actuel, peu de lignes)
FULL_REFRESH_TABLES = {"raw_repos", "raw_contributors", "raw_users"}

# Tables incrementales (on ajoute seulement les nouvelles lignes)
# cle naturelle utilisee pour eviter les doublons via ON CONFLICT
INCREMENTAL_KEYS = {
    "raw_commits": ("data->>'sha'", "text"),
    "raw_pull_requests": ("data->>'id'", "bigint"),
    "raw_issues": ("data->>'id'", "bigint"),
}


def get_latest_file(pattern):
    files = glob.glob(os.path.join(DATA_DIR, pattern))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def create_schema_and_tables(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        for table_name in TABLES:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS raw.{table_name} (
                    id SERIAL PRIMARY KEY,
                    loaded_at TIMESTAMP DEFAULT NOW(),
                    data JSONB NOT NULL
                );
            """)
        # index unique sur la cle naturelle, pour les tables incrementales uniquement
        for table_name, (expr, cast_type) in INCREMENTAL_KEYS.items():
            index_name = f"{table_name}_natural_key_idx"
            cur.execute(f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                ON raw.{table_name} ((({expr})::{cast_type}));
            """)
    conn.commit()
    print("Schema 'raw', tables et index uniques crees (ou deja existants).")


def load_json_to_table_full_refresh(conn, table_name, file_path):
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE raw.{table_name};")
    conn.commit()

    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    with conn.cursor() as cur:
        for record in records:
            cur.execute(
                f"INSERT INTO raw.{table_name} (data) VALUES (%s);",
                (Json(record),)
            )
    conn.commit()
    print(f"  [Full refresh] {len(records)} lignes chargees dans raw.{table_name}")


def load_json_to_table_incremental(conn, table_name, file_path, expr, cast_type):
    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    inserted = 0
    with conn.cursor() as cur:
        for record in records:
            cur.execute(
                f"""
                INSERT INTO raw.{table_name} (data)
                VALUES (%s)
                ON CONFLICT ((({expr})::{cast_type})) DO NOTHING;
                """,
                (Json(record),)
            )
            inserted += cur.rowcount
    conn.commit()
    print(f"  [Incremental] {inserted} nouvelles lignes inserees dans raw.{table_name} "
          f"({len(records) - inserted} doublons ignores)")


def get_all_files(pattern):
    """All files matching the pattern, oldest first."""
    return sorted(glob.glob(os.path.join(DATA_DIR, pattern)), key=os.path.getmtime)


def main(load_all=False):
    """load_all=True replays every incremental extract (oldest first), e.g. to rebuild an
    empty database. It is safe to re-run: ON CONFLICT DO NOTHING ignores known rows."""
    conn = psycopg2.connect(**DB_CONFIG)
    create_schema_and_tables(conn)

    for table_name, pattern in TABLES.items():
        latest_file = get_latest_file(pattern)
        if latest_file is None:
            print(f"Aucun fichier trouve pour {pattern}, ignore.")
            continue

        if table_name in FULL_REFRESH_TABLES:
            print(f"Chargement {table_name} depuis {os.path.basename(latest_file)}")
            load_json_to_table_full_refresh(conn, table_name, latest_file)
        else:
            expr, cast_type = INCREMENTAL_KEYS[table_name]
            files = get_all_files(pattern) if load_all else [latest_file]
            for file_path in files:
                print(f"Chargement {table_name} depuis {os.path.basename(file_path)}")
                load_json_to_table_incremental(conn, table_name, file_path, expr, cast_type)

    conn.close()
    print("Chargement termine.")


if __name__ == "__main__":
    import sys
    main(load_all="--all" in sys.argv)