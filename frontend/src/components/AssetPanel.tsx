import type { Asset } from "../types";
import { Navigation, Plane, Truck, Circle, BatteryWarning } from "lucide-react";

interface AssetPanelProps {
  assets: Asset[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

const STATUS_LABELS: Record<string, string> = {
  idle: "IDLE", en_route: "EN ROUTE", loitering: "LOITER", rtb: "RTB",
  low_battery: "LOW BAT", critical: "CRITICAL", offline: "OFFLINE",
  destroyed: "DESTROYED", mission_complete: "COMPLETE",
};

const STATUS_CLASSES: Record<string, string> = {
  idle: "text-aegis-text-muted", en_route: "text-aegis-accent", loitering: "text-aegis-success",
  rtb: "text-aegis-warning", low_battery: "text-aegis-warning", critical: "text-aegis-danger",
  offline: "text-aegis-text-muted", destroyed: "text-aegis-danger", mission_complete: "text-aegis-success",
};

function AssetIcon({ type }: { type: string }) {
  const cls = "w-4 h-4";
  switch (type) {
    case "quadrotor": return <Navigation className={cls} />;
    case "fixed_wing": return <Plane className={cls} />;
    case "ground_rover": return <Truck className={cls} />;
    default: return <Circle className={cls} />;
  }
}

export function AssetPanel({ assets, selectedId, onSelect }: AssetPanelProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="panel-header flex items-center justify-between">
        <span>Assets ({assets.length})</span>
        {selectedId && (
          <button
            onClick={() => onSelect(null)}
            className="text-[9px] text-aegis-text-muted hover:text-aegis-accent transition-colors"
          >
            CLEAR
          </button>
        )}
      </div>
      <div className="flex-1 overflow-y-auto">
        {assets.length === 0 && (
          <div className="p-4 text-center text-aegis-text-muted text-xs font-mono">
            No assets loaded
          </div>
        )}
        {assets.map((asset) => {
          const isSelected = asset.id === selectedId;
          return (
            <div
              key={asset.id}
              onClick={() => onSelect(isSelected ? null : asset.id)}
              className={`px-3 py-2.5 border-b border-aegis-border cursor-pointer transition-all ${
                isSelected
                  ? "bg-aegis-accent/10 border-l-2 border-l-aegis-accent"
                  : "hover:bg-aegis-panel/50 border-l-2 border-l-transparent"
              }`}
            >
              {/* Row 1: icon, callsign, status */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={STATUS_CLASSES[asset.status] ?? "text-aegis-text-muted"}>
                    <AssetIcon type={asset.type} />
                  </span>
                  <span className={`text-sm font-mono font-semibold ${isSelected ? "text-aegis-accent" : ""}`}>
                    {asset.callsign}
                  </span>
                </div>
                <span className={`text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded ${STATUS_CLASSES[asset.status] ?? ""}`}>
                  {STATUS_LABELS[asset.status] ?? asset.status.toUpperCase()}
                </span>
              </div>

              {/* Row 2: battery + position */}
              <div className="mt-1.5 flex items-center gap-3">
                <div className="flex items-center gap-1.5 min-w-[80px]">
                  {asset.battery_pct <= 20 && (
                    <BatteryWarning className="w-3 h-3 text-aegis-danger" />
                  )}
                  <div className="flex-1 h-1.5 bg-aegis-border rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        asset.battery_pct > 50 ? "bg-aegis-success"
                          : asset.battery_pct > 20 ? "bg-aegis-warning"
                          : "bg-aegis-danger"
                      }`}
                      style={{ width: `${asset.battery_pct}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-aegis-text-dim w-8 text-right">
                    {Math.round(asset.battery_pct)}%
                  </span>
                </div>
                <span className="text-[10px] font-mono text-aegis-text-muted">
                  ({asset.position.x.toFixed(0)}, {asset.position.y.toFixed(0)})
                </span>
              </div>

              {/* Row 3: speed + heading + waypoints */}
              <div className="mt-1 flex items-center gap-3 text-[10px] font-mono text-aegis-text-muted">
                <span>{asset.speed_mps.toFixed(1)} m/s</span>
                <span>HDG {asset.heading_deg.toFixed(0)}°</span>
                <span>WP {asset.waypoints_completed}/{asset.waypoints_completed + asset.waypoints_remaining}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
