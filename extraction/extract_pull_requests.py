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
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("SELECT MAX((data->>'created_at')::timestamp) FROM raw.raw_pull_requests")
        result = cur.fetchone()[0]
    conn.close()
    return result


def extract_pull_requests(max_pages_per_repo=5):
    client = GitHubClient()
    watermark = get_watermark()
    watermark_str = watermark.isoformat() + "Z" if watermark else None

    if watermark_str:
        print(f"Extraction incrementale depuis {watermark_str}")
    else:
        print("Aucune donnee existante -> extraction complete (premier run)")

    all_prs = []
    for repo in REPOS:
        print(f"Extraction PRs: {repo}")
        page = 1
        stop = False
        repo_prs = []

        while not stop and page <= max_pages_per_repo:
            response = client.get(
                f"/repos/{repo}/pulls",
                params={"state": "all", "sort": "created", "direction": "desc",
                        "per_page": 100, "page": page}
            )
            data = response.json()
            if not data:
                break

            for pr in data:
                if watermark_str and pr["created_at"] <= watermark_str:
                    stop = True
                    break
                repo_prs.append(pr)

            page += 1

        for pr in repo_prs:
            pr["_source_repo"] = repo

        all_prs.extend(repo_prs)
        print(f"  -> {len(repo_prs)} nouvelles PRs pour {repo}")

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")
    os.makedirs(DATA_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATA_DIR, f"pull_requests_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_prs, f, indent=2)

    print(f"{len(all_prs)} nouvelles PRs sauvegardees dans {output_path}")
    return output_path


if __name__ == "__main__":
    extract_pull_requests(max_pages_per_repo=5)