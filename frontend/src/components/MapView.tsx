import { useRef, useEffect } from "react";
import type { Asset } from "../types";

interface MapViewProps {
  assets: Asset[];
  worldWidth: number;
  worldHeight: number;
}

const STATUS_COLORS: Record<string, string> = {
  en_route: "#3b82f6",
  loitering: "#22c55e",
  rtb: "#f59e0b",
  idle: "#64748b",
  low_battery: "#f59e0b",
  critical: "#ef4444",
  offline: "#475569",
  mission_complete: "#22c55e",
  destroyed: "#dc2626",
};

/**
 * Tactical map — draws all assets, their headings, waypoints, and routes
 * on an HTML5 Canvas. Redraws every time the asset list updates (every tick).
 */
export function MapView({ assets, worldWidth, worldHeight }: MapViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    // Size canvas to container
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const scaleX = rect.width / worldWidth;
    const scaleY = rect.height / worldHeight;

    // Clear
    ctx.fillStyle = "#0a0e17";
    ctx.fillRect(0, 0, rect.width, rect.height);

    // Draw grid
    ctx.strokeStyle = "#1a2234";
    ctx.lineWidth = 1;
    const gridSpacing = 100; // meters
    for (let x = 0; x <= worldWidth; x += gridSpacing) {
      const px = x * scaleX;
      ctx.beginPath();
      ctx.moveTo(px, 0);
      ctx.lineTo(px, rect.height);
      ctx.stroke();
    }
    for (let y = 0; y <= worldHeight; y += gridSpacing) {
      const py = y * scaleY;
      ctx.beginPath();
      ctx.moveTo(0, py);
      ctx.lineTo(rect.width, py);
      ctx.stroke();
    }

    // Draw each asset
    for (const asset of assets) {
      const ax = asset.position.x * scaleX;
      const ay = asset.position.y * scaleY;
      const color = STATUS_COLORS[asset.status] ?? "#64748b";

      // Draw waypoint path
      if (asset.waypoints.length > 0) {
        ctx.strokeStyle = color + "40"; // 25% opacity
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        for (const wp of asset.waypoints) {
          ctx.lineTo(wp.x * scaleX, wp.y * scaleY);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw waypoint dots
        for (const wp of asset.waypoints) {
          ctx.fillStyle = color + "60";
          ctx.beginPath();
          ctx.arc(wp.x * scaleX, wp.y * scaleY, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Draw heading indicator line
      const headingRad = (asset.heading_deg * Math.PI) / 180;
      const lineLen = 18;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(
        ax + Math.sin(headingRad) * lineLen,
        ay - Math.cos(headingRad) * lineLen
      );
      ctx.stroke();

      // Draw asset body (triangle pointing in heading direction)
      const size = 7;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.save();
      ctx.translate(ax, ay);
      ctx.rotate(headingRad);
      ctx.moveTo(0, -size);
      ctx.lineTo(-size * 0.6, size * 0.5);
      ctx.lineTo(size * 0.6, size * 0.5);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Draw callsign label
      ctx.fillStyle = "#e2e8f0";
      ctx.font = "10px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText(asset.callsign, ax, ay + 18);

      // Battery bar below callsign
      const barWidth = 24;
      const barHeight = 3;
      const barX = ax - barWidth / 2;
      const barY = ay + 21;

      ctx.fillStyle = "#1a2234";
      ctx.fillRect(barX, barY, barWidth, barHeight);

      const batteryColor =
        asset.battery_pct > 50 ? "#22c55e" :
        asset.battery_pct > 20 ? "#f59e0b" : "#ef4444";
      ctx.fillStyle = batteryColor;
      ctx.fillRect(barX, barY, barWidth * (asset.battery_pct / 100), barHeight);
    }

    // Scale bar in bottom-left
    ctx.fillStyle = "#64748b";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    const scaleBarMeters = 100;
    const scaleBarPx = scaleBarMeters * scaleX;
    ctx.fillRect(12, rect.height - 20, scaleBarPx, 2);
    ctx.fillText(`${scaleBarMeters}m`, 12, rect.height - 24);
  }, [assets, worldWidth, worldHeight]);

  return (
    <div ref={containerRef} className="w-full h-full relative">
      <canvas ref={canvasRef} className="absolute inset-0" />
      {assets.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-aegis-text-muted text-sm font-mono">
          AWAITING TELEMETRY...
        </div>
      )}
    </div>
  );
}
