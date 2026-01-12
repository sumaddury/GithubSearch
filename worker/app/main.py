import argparse
from datetime import datetime, timezone

from sqlalchemy import text

from .db import SessionLocal
from .github import paginate
from .index import upsert_documents
from .normalize import clean_text


def parse_repo(repo: str) -> tuple[str, str]:
    repo = repo.strip()
    if repo.startswith("https://github.com/"):
        repo = repo.replace("https://github.com/", "")
    owner, name = repo.split("/", 1)
    return owner, name


def upsert_repository(db, repo_data):
    stmt = text(
        """
        INSERT INTO repository (id, owner, name, full_name, html_url, default_branch, last_ingested_at)
        VALUES (:id, :owner, :name, :full_name, :html_url, :default_branch, :last_ingested_at)
        ON CONFLICT (id) DO UPDATE SET
          owner = EXCLUDED.owner,
          name = EXCLUDED.name,
          full_name = EXCLUDED.full_name,
          html_url = EXCLUDED.html_url,
          default_branch = EXCLUDED.default_branch,
          last_ingested_at = EXCLUDED.last_ingested_at
        """
    )
    db.execute(
        stmt,
        {
            "id": repo_data["id"],
            "owner": repo_data["owner"]["login"],
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "html_url": repo_data["html_url"],
            "default_branch": repo_data["default_branch"],
            "last_ingested_at": datetime.now(timezone.utc),
        },
    )


def upsert_issue(db, repo_id: int, issue):
    labels = ",".join([l["name"] for l in issue.get("labels", [])])
    stmt = text(
        """
        INSERT INTO issue (id, repo_id, number, title, body, state, labels, author,
                           is_pull_request, comments_count, created_at, updated_at, html_url)
        VALUES (:id, :repo_id, :number, :title, :body, :state, :labels, :author,
                :is_pull_request, :comments_count, :created_at, :updated_at, :html_url)
        ON CONFLICT (id) DO UPDATE SET
          title = EXCLUDED.title,
          body = EXCLUDED.body,
          state = EXCLUDED.state,
          labels = EXCLUDED.labels,
          author = EXCLUDED.author,
          is_pull_request = EXCLUDED.is_pull_request,
          comments_count = EXCLUDED.comments_count,
          created_at = EXCLUDED.created_at,
          updated_at = EXCLUDED.updated_at,
          html_url = EXCLUDED.html_url
        """
    )
    db.execute(
        stmt,
        {
            "id": issue["id"],
            "repo_id": repo_id,
            "number": issue["number"],
            "title": issue.get("title"),
            "body": issue.get("body"),
            "state": issue.get("state"),
            "labels": labels,
            "author": issue.get("user", {}).get("login"),
            "is_pull_request": "pull_request" in issue,
            "comments_count": issue.get("comments", 0),
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
            "html_url": issue.get("html_url"),
        },
    )


def upsert_comment(db, repo_id: int, issue_id: int, comment):
    stmt = text(
        """
        INSERT INTO comment (id, issue_id, repo_id, body, author, created_at, updated_at, html_url)
        VALUES (:id, :issue_id, :repo_id, :body, :author, :created_at, :updated_at, :html_url)
        ON CONFLICT (id) DO UPDATE SET
          body = EXCLUDED.body,
          author = EXCLUDED.author,
          created_at = EXCLUDED.created_at,
          updated_at = EXCLUDED.updated_at,
          html_url = EXCLUDED.html_url
        """
    )
    db.execute(
        stmt,
        {
            "id": comment["id"],
            "issue_id": issue_id,
            "repo_id": repo_id,
            "body": comment.get("body"),
            "author": comment.get("user", {}).get("login"),
            "created_at": comment.get("created_at"),
            "updated_at": comment.get("updated_at"),
            "html_url": comment.get("html_url"),
        },
    )


def issue_to_doc(repo_full_name: str, issue):
    labels = [l["name"] for l in issue.get("labels", [])]
    return {
        "id": f"issue:{issue['id']}",
        "repo_full_name": repo_full_name,
        "type": "pr" if "pull_request" in issue else "issue",
        "title": clean_text(issue.get("title")),
        "body": clean_text(issue.get("body")),
        "labels": labels,
        "author": issue.get("user", {}).get("login"),
        "created_at": issue.get("created_at"),
        "html_url": issue.get("html_url"),
        "issue_number": issue.get("number"),
    }


def comment_to_doc(repo_full_name: str, issue_number: int, comment):
    return {
        "id": f"comment:{comment['id']}",
        "repo_full_name": repo_full_name,
        "type": "comment",
        "title": None,
        "body": clean_text(comment.get("body")),
        "labels": [],
        "author": comment.get("user", {}).get("login"),
        "created_at": comment.get("created_at"),
        "html_url": comment.get("html_url"),
        "issue_number": issue_number,
    }


def ingest_repo(repo: str):
    owner, name = parse_repo(repo)
    repo_url = f"https://api.github.com/repos/{owner}/{name}"
    issues_url = f"https://api.github.com/repos/{owner}/{name}/issues"

    docs = []

    with SessionLocal() as db:
        repo_data = next(paginate(repo_url))
        upsert_repository(db, repo_data)

        for issue in paginate(issues_url, params={"state": "all", "per_page": 100}):
            if issue.get("pull_request") or issue.get("title"):
                upsert_issue(db, repo_data["id"], issue)
                docs.append(issue_to_doc(repo_data["full_name"], issue))

            comments_url = issue.get("comments_url")
            if comments_url and issue.get("comments", 0) > 0:
                for comment in paginate(comments_url, params={"per_page": 100}):
                    upsert_comment(db, repo_data["id"], issue["id"], comment)
                    docs.append(comment_to_doc(repo_data["full_name"], issue["number"], comment))

        db.commit()

    upsert_documents(docs)


def main():
    parser = argparse.ArgumentParser(description="GitHub ingestion worker")
    parser.add_argument("--repo", required=True, help="owner/repo or GitHub URL")
    args = parser.parse_args()
    ingest_repo(args.repo)


if __name__ == "__main__":
    main()
