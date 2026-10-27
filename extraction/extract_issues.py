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
        cur.execute("SELECT MAX((data->>'created_at')::timestamp) FROM raw.raw_issues")
        result = cur.fetchone()[0]
    conn.close()
    return result


def extract_issues(max_pages_per_repo=5):
    """Note: l'endpoint /issues renvoie aussi les PRs (filtre sur 'pull_request')."""
    client = GitHubClient()
    watermark = get_watermark()
    watermark_str = watermark.isoformat() + "Z" if watermark else None

    if watermark_str:
        print(f"Extraction incrementale depuis {watermark_str}")
    else:
        print("Aucune donnee existante -> extraction complete (premier run)")

    all_issues = []
    for repo in REPOS:
        print(f"Extraction issues: {repo}")
        page = 1
        stop = False
        repo_issues = []

        while not stop and page <= max_pages_per_repo:
            response = client.get(
                f"/repos/{repo}/issues",
                params={"state": "all", "sort": "created", "direction": "desc",
                        "per_page": 100, "page": page}
            )
            data = response.json()
            if not data:
                break

            for item in data:
                if "pull_request" in item:
                    continue  # on ignore les PRs melangees dans /issues

                if watermark_str and item["created_at"] <= watermark_str:
                    stop = True
                    break
                repo_issues.append(item)

            page += 1

        for issue in repo_issues:
            issue["_source_repo"] = repo

        all_issues.extend(repo_issues)
        print(f"  -> {len(repo_issues)} nouvelles issues pour {repo}")

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")
    os.makedirs(DATA_DIR, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATA_DIR, f"issues_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_issues, f, indent=2)

    print(f"{len(all_issues)} nouvelles issues sauvegardees dans {output_path}")
    return output_path


if __name__ == "__main__":
    extract_issues(max_pages_per_repo=5)