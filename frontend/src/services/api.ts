/**
 * AEGIS API client — thin wrapper around fetch for REST endpoints.
 *
 * In development, Vite proxies /api/* to FastAPI at localhost:8000.
 */

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/* ── Health ──────────────────────────────────────────── */

export async function getHealth() {
  return request<{ status: string; service: string; version: string }>("/health");
}

/* ── Missions ────────────────────────────────────────── */

export async function getMissions() {
  return request<{ missions: Array<Record<string, unknown>> }>("/missions");
}

export async function getMission(id: string) {
  return request<Record<string, unknown>>(`/missions/${id}`);
}

/* ── Assets ──────────────────────────────────────────── */

export async function getAssets() {
  return request<{ assets: Array<Record<string, unknown>> }>("/assets");
}

/* ── Commands ────────────────────────────────────────── */

export async function submitCommand(text: string, missionId = "mission-001") {
  return request<Record<string, unknown>>("/commands", {
    method: "POST",
    body: JSON.stringify({ text, mission_id: missionId }),
  });
}
