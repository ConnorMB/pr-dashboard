const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getMetric(path,repoId) {
  const response = await fetch(`${API_URL}${path}?repo_id=${repoId}`);
  if (!response.ok) throw new Error(`Request failed: ${path}`);
  return response.json();
}

// submits a repo to get synced, backend handles rate limiting/caching on its end
export async function createOrSyncRepo(owner, name) {
  const response = await fetch(`${API_URL}/repos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ owner, name }),
  });
  if (response.status === 429) {
    throw new Error("Too many repos requested, try again in a bit");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "could not load that repo");
  }
  return response.json();
}

// checks in on a repo's sync status, this is what gets polled
export async function getRepoStatus(repoId) {
  const response = await fetch(`${API_URL}/repos/${repoId}`);
  if (!response.ok) throw new Error("could not check repo status");
  return response.json();
}