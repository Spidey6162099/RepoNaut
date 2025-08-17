const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080';

export async function ingest(repo_url) {
  const fd = new FormData();
  fd.append('github_url', repo_url);
  const res = await fetch(`${API_BASE}/ingest`, { method: 'POST', body: fd });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function ask(query, k=6) {
  const fd = new FormData();
  fd.append('query', query);
  fd.append('k', String(k));
  const res = await fetch(`${API_BASE}/query`, { method: 'POST', body: fd });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
