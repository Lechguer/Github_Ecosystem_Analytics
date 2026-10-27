import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubClient:
    def __init__(self):
        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN manquant dans .env")
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _check_rate_limit(self, response):
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

        if remaining < 5:
            wait_seconds = max(reset_time - time.time(), 0) + 1
            print(f"Rate limit presque atteint. Attente de {wait_seconds:.0f}s...")
            time.sleep(wait_seconds)

    def get(self, endpoint, params=None):
        
        url = f"{BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        self._check_rate_limit(response)

        if response.status_code != 200:
            raise Exception(f"Erreur API {response.status_code}: {response.text}")

        return response

    def get_paginated(self, endpoint, params=None, max_pages=None):
        
        if params is None:
            params = {}
        params["per_page"] = 100

        all_results = []
        page = 1

        while True:
            params["page"] = page
            response = self.get(endpoint, params=params)
            data = response.json()

            if not data:
                break

            all_results.extend(data)
            print(f"  Page {page} récupérée ({len(data)} items)")

            if max_pages and page >= max_pages:
                break

            if 'next' not in response.links:
                break

            page += 1

        return all_results