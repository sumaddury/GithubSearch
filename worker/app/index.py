from meilisearch import Client

from .config import settings

INDEX_NAME = "github_items"


def get_client():
    return Client(settings.meili_host, settings.meili_api_key)


def ensure_index():
    client = get_client()
    try:
        client.get_index(INDEX_NAME)
    except Exception:
        client.create_index(INDEX_NAME, {"primaryKey": "id"})
    index = client.index(INDEX_NAME)
    index.update_searchable_attributes(["title", "body", "labels", "author"])
    index.update_filterable_attributes(["repo_full_name", "type", "labels"])
    index.update_sortable_attributes(["created_at"])
    return index


def upsert_documents(documents: list[dict]):
    index = ensure_index()
    if documents:
        index.add_documents(documents)
