import type { MissionSummary } from "../types";
import { Activity, Battery, AlertTriangle, Radio } from "lucide-react";

interface SystemHealthProps {
  mission: MissionSummary | null;
  status: string;
}

/**
 * Compact overview panel showing key mission metrics at a glance.
 */
export function SystemHealth({ mission, status }: SystemHealthProps) {
  const stats = mission ?? {
    total_assets: 0,
    active_assets: 0,
    idle_assets: 0,
    avg_battery_pct: 0,
    active_alerts: 0,
  };

  return (
    <div>
      <div className="panel-header">System Status</div>
      <div className="p-3 grid grid-cols-2 gap-2">
        <StatCard
          icon={<Activity className="w-3.5 h-3.5" />}
          label="Active"
          value={`${stats.active_assets}/${stats.total_assets}`}
          color="text-aegis-success"
        />
        <StatCard
          icon={<Battery className="w-3.5 h-3.5" />}
          label="Avg Battery"
          value={`${Math.round(stats.avg_battery_pct)}%`}
          color={
            stats.avg_battery_pct > 50
              ? "text-aegis-success"
              : stats.avg_battery_pct > 20
              ? "text-aegis-warning"
              : "text-aegis-danger"
          }
        />
        <StatCard
          icon={<AlertTriangle className="w-3.5 h-3.5" />}
          label="Alerts"
          value={String(stats.active_alerts)}
          color={stats.active_alerts > 0 ? "text-aegis-warning" : "text-aegis-text-dim"}
        />
        <StatCard
          icon={<Radio className="w-3.5 h-3.5" />}
          label="Uplink"
          value={status === "connected" ? "NOMINAL" : "LOST"}
          color={status === "connected" ? "text-aegis-success" : "text-aegis-danger"}
        />
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="bg-aegis-bg/50 rounded px-2.5 py-2 border border-aegis-border/50">
      <div className="flex items-center gap-1.5 text-aegis-text-muted mb-1">
        {icon}
        <span className="text-[10px] font-mono uppercase">{label}</span>
      </div>
      <span className={`text-sm font-mono font-semibold ${color}`}>{value}</span>
    </div>
  );
}
