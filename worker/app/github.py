import time
from typing import Generator

import requests

from .config import settings


API_BASE = "https://api.github.com"


def github_headers():
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def handle_rate_limit(resp: requests.Response):
    if resp.status_code != 403:
        return
    reset = resp.headers.get("X-RateLimit-Reset")
    if reset:
        sleep_for = max(0, int(reset) - int(time.time())) + 1
        time.sleep(sleep_for)


def paginate(url: str, params: dict | None = None) -> Generator[dict, None, None]:
    session = requests.Session()
    while url:
        resp = session.get(url, headers=github_headers(), params=params)
        if resp.status_code == 403:
            handle_rate_limit(resp)
            resp = session.get(url, headers=github_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            for item in data:
                yield item
        else:
            yield data
        url = None
        params = None
        link = resp.headers.get("Link", "")
        for part in link.split(","):
            if "rel=\"next\"" in part:
                url = part.split(";")[0].strip().strip("<>")
                break
