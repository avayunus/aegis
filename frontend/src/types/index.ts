/* ─── Core domain types ──────────────────────────────────────────── */

export interface Position {
  x: number;
  y: number;
}

export interface WaypointData {
  x: number;
  y: number;
  label: string;
}

export type AssetStatus =
  | "idle"
  | "en_route"
  | "loitering"
  | "rtb"
  | "low_battery"
  | "critical"
  | "offline"
  | "destroyed"
  | "mission_complete";

export type VehicleType = "quadrotor" | "fixed_wing" | "ground_rover";

export interface Asset {
  id: string;
  callsign: string;
  type: VehicleType;
  status: AssetStatus;
  position: Position;
  heading_deg: number;
  speed_mps: number;
  battery_pct: number;
  waypoints_completed: number;
  waypoints_remaining: number;
  waypoints: WaypointData[];
}

export type AlertSeverity = "info" | "warning" | "critical";

export interface Alert {
  id: string;
  vehicle_id: string;
  type: string;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface MissionSummary {
  total_assets: number;
  active_assets: number;
  idle_assets: number;
  avg_battery_pct: number;
  active_alerts: number;
}

/* ─── WebSocket telemetry frame ──────────────────────────────────── */

export interface TelemetryFrame {
  tick: number;
  timestamp: string;
  paused: boolean;
  elapsed_seconds: number;
  mission_id: string | null;
  mission_name: string;
  world: {
    width: number;
    height: number;
  };
  assets: Asset[];
  alerts: Alert[];
  mission: MissionSummary;
}

/* ─── Command types ──────────────────────────────────────────────── */

export type RiskLevel = "low" | "medium" | "high" | "blocked";

export interface CommandRecord {
  id: number;
  raw_text: string;
  interpreted_intent: string | null;
  risk_level: RiskLevel;
  status: string;
  result_summary: string | null;
  requires_approval: boolean;
  created_at: string;
}
