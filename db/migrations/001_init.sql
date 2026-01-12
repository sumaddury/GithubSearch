CREATE TABLE IF NOT EXISTS repository (
  id BIGINT PRIMARY KEY,
  owner TEXT NOT NULL,
  name TEXT NOT NULL,
  full_name TEXT NOT NULL UNIQUE,
  html_url TEXT NOT NULL,
  default_branch TEXT NOT NULL,
  last_ingested_at TIMESTAMP WITH TIME ZONE,
  last_cursor TEXT
);

CREATE TABLE IF NOT EXISTS issue (
  id BIGINT PRIMARY KEY,
  repo_id BIGINT NOT NULL REFERENCES repository(id),
  number INT NOT NULL,
  title TEXT,
  body TEXT,
  state TEXT,
  labels TEXT,
  author TEXT,
  is_pull_request BOOLEAN DEFAULT FALSE,
  comments_count INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  html_url TEXT
);

CREATE TABLE IF NOT EXISTS comment (
  id BIGINT PRIMARY KEY,
  issue_id BIGINT NOT NULL REFERENCES issue(id),
  repo_id BIGINT NOT NULL REFERENCES repository(id),
  body TEXT,
  author TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  html_url TEXT
);
