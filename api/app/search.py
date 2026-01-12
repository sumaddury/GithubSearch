from meilisearch import Client

from .config import settings


INDEX_NAME = "github_items"


def get_client():
    return Client(settings.meili_host, settings.meili_api_key)


def search_index(repo: str, query: str, item_type: str | None = None, limit: int = 10):
    client = get_client()
    index = client.index(INDEX_NAME)
    filters = [f"repo_full_name = '{repo}'"]
    if item_type:
        filters.append(f"type = '{item_type}'")
    options = {
        "limit": limit,
        "filter": " AND ".join(filters),
    }
    return index.search(query, options)
