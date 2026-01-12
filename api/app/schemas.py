from typing import List, Optional
from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str
    type: str
    title: Optional[str] = None
    body: Optional[str] = None
    labels: List[str] = []
    author: Optional[str] = None
    created_at: Optional[str] = None
    html_url: Optional[str] = None
    issue_number: Optional[int] = None


class SearchResponse(BaseModel):
    query: str
    repo: str
    hits: List[SearchResult]
    total: int


class IngestRequest(BaseModel):
    repo: str
