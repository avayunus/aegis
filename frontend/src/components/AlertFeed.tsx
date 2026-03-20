import type { Alert } from "../types";
import { AlertTriangle, Info, AlertOctagon } from "lucide-react";

interface AlertFeedProps {
  alerts: Alert[];
}

const SEVERITY_ICON = {
  info: Info,
  warning: AlertTriangle,
  critical: AlertOctagon,
};

const SEVERITY_CLASS = {
  info: "text-aegis-accent",
  warning: "text-aegis-warning",
  critical: "text-aegis-danger",
};

/**
 * Scrollable feed of system alerts, newest first.
 * Shows anomaly detections, low battery warnings, comms loss, etc.
 */
export function AlertFeed({ alerts }: AlertFeedProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="panel-header flex items-center justify-between">
        <span>Alerts</span>
        {alerts.filter((a) => !a.acknowledged).length > 0 && (
          <span className="bg-aegis-danger/20 text-aegis-danger text-[10px] font-mono px-1.5 py-0.5 rounded">
            {alerts.filter((a) => !a.acknowledged).length} active
          </span>
        )}
      </div>
      <div className="flex-1 overflow-y-auto">
        {alerts.length === 0 && (
          <div className="p-4 text-center text-aegis-text-muted text-xs font-mono">
            No alerts
          </div>
        )}
        {alerts.map((alert) => {
          const Icon = SEVERITY_ICON[alert.severity] ?? Info;
          const colorClass = SEVERITY_CLASS[alert.severity] ?? "text-aegis-text-dim";

          return (
            <div
              key={alert.id}
              className={`px-3 py-2 border-b border-aegis-border flex items-start gap-2 ${
                alert.acknowledged ? "opacity-50" : ""
              }`}
            >
              <Icon className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${colorClass}`} />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-mono leading-snug">{alert.message}</p>
                <p className="text-[10px] text-aegis-text-muted font-mono mt-0.5">
                  {new Date(alert.timestamp).toLocaleTimeString()} · {alert.type}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
