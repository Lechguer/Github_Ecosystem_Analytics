import json
import os
from datetime import datetime, timezone
from github_client import GitHubClient

def extract_users():
    """
    Recupere le profil detaille de chaque contributeur unique
    (deduplique entre les 3 repos) via /users/{login}.
    """
    client = GitHubClient()

    # On relit le dernier fichier contributors_*.json pour recuperer
    # la liste des logins uniques (pas besoin de re-appeler /contributors)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw_json")

    contributors_files = [f for f in os.listdir(DATA_DIR) if f.startswith("contributors_")]
    latest_file = max(contributors_files)
    with open(os.path.join(DATA_DIR, latest_file), "r", encoding="utf-8") as f:
        contributors = json.load(f)

    unique_logins = sorted(set(c["login"] for c in contributors))
    print(f"{len(unique_logins)} contributeurs uniques a enrichir")

    all_users = []
    for i, login in enumerate(unique_logins, start=1):
        print(f"  [{i}/{len(unique_logins)}] {login}")
        response = client.get(f"/users/{login}")
        all_users.append(response.json())

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATA_DIR, f"users_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_users, f, indent=2)

    print(f"{len(all_users)} profils utilisateurs sauvegardes dans {output_path}")
    return output_path


if __name__ == "__main__":
    extract_users()