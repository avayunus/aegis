import { useState } from "react";
import type { Alert } from "../types";
import { AlertTriangle, Info, AlertOctagon, CheckCircle } from "lucide-react";

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

const SEVERITY_BG = {
  info: "",
  warning: "",
  critical: "bg-aegis-danger/5",
};

/**
 * Alert feed with acknowledge buttons.
 * Critical alerts pulse. Acknowledged alerts dim.
 */
export function AlertFeed({ alerts }: AlertFeedProps) {
  const [acknowledged, setAcknowledged] = useState<Set<string>>(new Set());

  const handleAck = (id: string) => {
    setAcknowledged((prev) => new Set([...prev, id]));
  };

  const activeCount = alerts.filter(
    (a) => !a.acknowledged && !acknowledged.has(a.id)
  ).length;

  return (
    <div className="flex flex-col h-full">
      <div className="panel-header flex items-center justify-between">
        <span>Alerts</span>
        {activeCount > 0 && (
          <span className="bg-aegis-danger/20 text-aegis-danger text-[10px] font-mono px-1.5 py-0.5 rounded animate-pulse">
            {activeCount} active
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
          const bgClass = SEVERITY_BG[alert.severity] ?? "";
          const isAcked = alert.acknowledged || acknowledged.has(alert.id);

          return (
            <div
              key={alert.id}
              className={`px-3 py-2 border-b border-aegis-border flex items-start gap-2 transition-opacity ${
                isAcked ? "opacity-40" : bgClass
              } ${alert.severity === "critical" && !isAcked ? "animate-pulse-slow" : ""}`}
            >
              <Icon className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${colorClass}`} />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-mono leading-snug">{alert.message}</p>
                <p className="text-[10px] text-aegis-text-muted font-mono mt-0.5">
                  {new Date(alert.timestamp).toLocaleTimeString()} · {alert.type}
                </p>
              </div>
              {!isAcked && (
                <button
                  onClick={() => handleAck(alert.id)}
                  className="flex-shrink-0 p-0.5 hover:bg-aegis-accent/10 rounded transition-colors"
                  title="Acknowledge"
                >
                  <CheckCircle className="w-3.5 h-3.5 text-aegis-text-muted hover:text-aegis-success" />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
