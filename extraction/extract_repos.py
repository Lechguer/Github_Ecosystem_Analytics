import json
import os
from datetime import datetime, timezone
from github_client import GitHubClient

REPOS = [
    "duckdb/duckdb",
    "dbt-labs/dbt-core",
    "apache/airflow",
]

def extract_repos():
    client = GitHubClient()
    results = []

    for repo in REPOS:
        print(f"Extraction repo: {repo}")
        response = client.get(f"/repos/{repo}")
        results.append(response.json())

    # Sauvegarde en JSON brut, horodaté
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")

    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, f"repos_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"{len(results)} repos sauvegardés dans {output_path}")
    return output_path


if __name__ == "__main__":
    extract_repos()