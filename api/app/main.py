from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
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
    if item_id.startswith("issue:"):
        raw_id = item_id.split(":", 1)[1]
        row = db.execute(text("SELECT * FROM issue WHERE id = :id"), {"id": raw_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Issue not found")
        return dict(row)
    if item_id.startswith("comment:"):
        raw_id = item_id.split(":", 1)[1]
        row = db.execute(text("SELECT * FROM comment WHERE id = :id"), {"id": raw_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Comment not found")
        return dict(row)
    raise HTTPException(status_code=400, detail="Invalid item id")


@app.post("/ingest")
def ingest(request: IngestRequest):
    # Placeholder: worker trigger will be wired after worker is running.
    return {"status": "queued", "repo": request.repo}


@app.get("/status")
def status(repo: str, db: Session = Depends(get_db)):
    repo_row = db.execute(
        text("SELECT id, last_ingested_at FROM repository WHERE full_name = :repo"),
        {"repo": repo},
    ).mappings().first()
    if not repo_row:
        return {"repo": repo, "last_ingested_at": None, "issues": 0, "comments": 0}
    repo_id = repo_row["id"]
    issues = db.execute(text("SELECT COUNT(*) FROM issue WHERE repo_id = :repo_id"), {"repo_id": repo_id}).scalar()
    comments = db.execute(text("SELECT COUNT(*) FROM comment WHERE repo_id = :repo_id"), {"repo_id": repo_id}).scalar()
    return {
        "repo": repo,
        "last_ingested_at": repo_row["last_ingested_at"],
        "issues": issues,
        "comments": comments,
    }
