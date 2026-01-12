from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repository"

    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False, unique=True)
    html_url = Column(String, nullable=False)
    default_branch = Column(String, nullable=False)
    last_ingested_at = Column(DateTime)
    last_cursor = Column(String)


class Issue(Base):
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey("repository.id"), nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String)
    body = Column(Text)
    state = Column(String)
    labels = Column(Text)
    author = Column(String)
    is_pull_request = Column(Boolean, default=False)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    html_url = Column(String)


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issue.id"), nullable=False)
    repo_id = Column(Integer, ForeignKey("repository.id"), nullable=False)
    body = Column(Text)
    author = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    html_url = Column(String)
