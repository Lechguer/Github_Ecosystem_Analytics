import json
import os
from datetime import datetime, timezone
from github_client import GitHubClient

REPOS = [
    "duckdb/duckdb",
    "dbt-labs/dbt-core",
    "apache/airflow",
]

def extract_contributors(max_pages_per_repo=3):
    client = GitHubClient()
    all_contributors = []

    for repo in REPOS:
        print(f"Extraction contributors: {repo}")
        contributors = client.get_paginated(
            f"/repos/{repo}/contributors",
            max_pages=max_pages_per_repo
        )

        for c in contributors:
            c["_source_repo"] = repo

        all_contributors.extend(contributors)
        print(f"  → {len(contributors)} contributeurs récupérés pour {repo}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")

    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, f"contributors_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_contributors, f, indent=2)

    print(f"{len(all_contributors)} contributeurs sauvegardés dans {output_path}")
    return output_path


if __name__ == "__main__":
    extract_contributors(max_pages_per_repo=3)