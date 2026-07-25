const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getMetric(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) throw new Error(`Request failed: ${path}`);
  return response.json();
}

export async function triggerSync() {
  const response = await fetch(`${API_URL}/ingest`, { method: "POST" });
  if (!response.ok) throw new Error("Sync failed");
  return response.json();
}