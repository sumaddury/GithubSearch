import React, { useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [repo, setRepo] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const onSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    const params = new URLSearchParams({ repo, q: query });
    const resp = await fetch(`${API_BASE}/search?${params.toString()}`);
    const data = await resp.json();
    setResults(data.hits || []);
    setLoading(false);
  };

  return (
    <div style={{ fontFamily: "Georgia, serif", padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h1 style={{ fontSize: "2.4rem", marginBottom: "0.5rem" }}>GitHub Issues Search</h1>
      <p style={{ color: "#555" }}>Search a public repository by describing your issue.</p>
      <form onSubmit={onSearch} style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
        <input
          value={repo}
          onChange={(e) => setRepo(e.target.value)}
          placeholder="owner/repo or GitHub URL"
          style={{ padding: "0.6rem", fontSize: "1rem" }}
        />
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your issue"
          rows={4}
          style={{ padding: "0.6rem", fontSize: "1rem" }}
        />
        <button type="submit" style={{ padding: "0.75rem", fontSize: "1rem" }}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      <div style={{ marginTop: "2rem" }}>
        {results.map((item) => (
          <div key={item.id} style={{ padding: "1rem", borderBottom: "1px solid #ddd" }}>
            <div style={{ fontSize: "0.8rem", color: "#666" }}>
              {item.type} • {item.author}
            </div>
            {item.title && <div style={{ fontWeight: 600 }}>{item.title}</div>}
            {item.body && <div style={{ color: "#333" }}>{item.body.slice(0, 200)}...</div>}
            {item.html_url && (
              <a href={item.html_url} target="_blank" rel="noreferrer">
                View on GitHub
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
