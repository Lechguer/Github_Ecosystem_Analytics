import json
import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv
from github_client import GitHubClient

load_dotenv()

REPOS = [
    "duckdb/duckdb",
    "dbt-labs/dbt-core",
    "apache/airflow",
]

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


def get_watermark():
    """Date du commit le plus recent deja en base. None si table vide (premier run)."""
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MAX((data->'commit'->'author'->>'date')::timestamp)
            FROM raw.raw_commits
        """)
        result = cur.fetchone()[0]
    conn.close()
    return result


def extract_commits(max_pages_per_repo=5):
    client = GitHubClient()
    watermark = get_watermark()
    since_param = watermark.isoformat() + "Z" if watermark else None

    if since_param:
        print(f"Extraction incrementale depuis {since_param}")
    else:
        print("Aucune donnee existante -> extraction complete (premier run)")

    all_commits = []
    for repo in REPOS:
        print(f"Extraction commits: {repo}")
        params = {"since": since_param} if since_param else {}

        commits = client.get_paginated(
            f"/repos/{repo}/commits",
            params=params,
            max_pages=max_pages_per_repo
        )

        for c in commits:
            c["_source_repo"] = repo

        all_commits.extend(commits)
        print(f"  -> {len(commits)} nouveaux commits pour {repo}")

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")
    os.makedirs(DATA_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATA_DIR, f"commits_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_commits, f, indent=2)

    print(f"{len(all_commits)} nouveaux commits sauvegardes dans {output_path}")
    return output_path


if __name__ == "__main__":
    extract_commits(max_pages_per_repo=5)