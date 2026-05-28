/**
 * Shared API base URL.
 * - Dev: empty string → Vite proxies /api and /health to localhost:8000
 * - Prod: set VITE_API_URL=https://your-api.example.com
 */
export const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  return fetch(url, init);
}
