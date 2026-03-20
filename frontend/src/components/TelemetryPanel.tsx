import type { Asset } from "../types";

interface TelemetryPanelProps {
  assets: Asset[];
}

/**
 * Detailed telemetry readout for all assets. Shows raw numbers
 * in a format inspired by real flight instrument readouts.
 */
export function TelemetryPanel({ assets }: TelemetryPanelProps) {
  return (
    <div>
      <div className="panel-header">Telemetry</div>
      <div className="divide-y divide-aegis-border/50">
        {assets.length === 0 && (
          <div className="p-3 text-center text-aegis-text-muted text-xs font-mono">
            No telemetry data
          </div>
        )}
        {assets.map((asset) => (
          <div key={asset.id} className="px-3 py-2">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-mono font-semibold text-aegis-text">
                {asset.callsign}
              </span>
              <span className="text-[10px] font-mono text-aegis-text-muted">
                {asset.type.toUpperCase()}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-x-3 gap-y-1 text-[10px] font-mono">
              <TelemetryValue label="POS X" value={asset.position.x.toFixed(1)} unit="m" />
              <TelemetryValue label="POS Y" value={asset.position.y.toFixed(1)} unit="m" />
              <TelemetryValue label="HDG" value={asset.heading_deg.toFixed(0)} unit="°" />
              <TelemetryValue label="SPD" value={asset.speed_mps.toFixed(1)} unit="m/s" />
              <TelemetryValue
                label="BAT"
                value={asset.battery_pct.toFixed(0)}
                unit="%"
                warn={asset.battery_pct < 30}
              />
              <TelemetryValue
                label="WPT"
                value={`${asset.waypoints_completed}/${asset.waypoints_completed + asset.waypoints_remaining}`}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TelemetryValue({
  label,
  value,
  unit,
  warn = false,
}: {
  label: string;
  value: string;
  unit?: string;
  warn?: boolean;
}) {
  return (
    <div>
      <span className="text-aegis-text-muted">{label} </span>
      <span className={warn ? "text-aegis-warning" : "text-aegis-text"}>
        {value}
      </span>
      {unit && <span className="text-aegis-text-muted">{unit}</span>}
    </div>
  );
}
