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
  return request<Record<string, unknown>>("/missions");
}

export async function getMissionState() {
  return request<Record<string, unknown>>("/missions/state");
}

export async function loadScenario(filename: string) {
  return request<Record<string, unknown>>("/missions/load", {
    method: "POST",
    body: JSON.stringify({ filename }),
  });
}

export async function pauseSimulation() {
  return request<Record<string, unknown>>("/missions/pause", { method: "POST" });
}

export async function resumeSimulation() {
  return request<Record<string, unknown>>("/missions/resume", { method: "POST" });
}

export async function resetSimulation() {
  return request<Record<string, unknown>>("/missions/reset", { method: "POST" });
}

/* ── Assets ──────────────────────────────────────────── */

export async function getAssets() {
  return request<{ count: number; assets: Array<Record<string, unknown>> }>("/assets");
}

export async function getAsset(id: string) {
  return request<Record<string, unknown>>(`/assets/${id}`);
}

export async function commandRtb(assetId: string) {
  return request<Record<string, unknown>>(`/assets/${assetId}/rtb`, { method: "POST" });
}

export async function commandHold(assetId: string) {
  return request<Record<string, unknown>>(`/assets/${assetId}/hold`, { method: "POST" });
}

/* ── Commands ────────────────────────────────────────── */

export interface CommandResponse {
  command_id: string;
  raw_text: string;
  risk_level: string;
  status: string;
  interpreted_intent: string;
  actions: Array<{ success?: boolean; message?: string }>;
  result_summary: string | null;
  requires_approval: boolean;
  ai_response: string | null;
  timestamp: string;
}

export async function submitCommand(text: string, missionId?: string) {
  return request<CommandResponse>("/commands", {
    method: "POST",
    body: JSON.stringify({ text, mission_id: missionId }),
  });
}

export async function getCommandHistory(limit = 50) {
  return request<{ commands: CommandResponse[]; total: number }>(`/commands/history?limit=${limit}`);
}

export async function approveCommand(commandId: string) {
  return request<Record<string, unknown>>(`/commands/${commandId}/approve`, { method: "POST" });
}

export async function rejectCommand(commandId: string) {
  return request<Record<string, unknown>>(`/commands/${commandId}/reject`, { method: "POST" });
}
