from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .schemas import IngestRequest, SearchResponse
from .search import search_index

app = FastAPI(title="GitHub Issues Search API")


@app.get("/search", response_model=SearchResponse)
def search(repo: str, q: str, type: str | None = None):
    result = search_index(repo=repo, query=q, item_type=type)
    hits = result.get("hits", [])
    return SearchResponse(query=q, repo=repo, hits=hits, total=result.get("estimatedTotalHits", 0))


@app.get("/items/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    # Placeholder: direct lookup from Postgres can be implemented later.
    raise HTTPException(status_code=501, detail="Item lookup not implemented yet")


@app.post("/ingest")
def ingest(request: IngestRequest):
    # Placeholder: worker trigger will be wired after worker is running.
    return {"status": "queued", "repo": request.repo}


@app.get("/status")
def status(repo: str, db: Session = Depends(get_db)):
    # Placeholder: return last_ingested_at and counts.
    return {"repo": repo, "last_ingested_at": None}
