import { useRef, useEffect, useCallback } from "react";
import type { Asset, Alert } from "../types";

interface MapViewProps {
  assets: Asset[];
  alerts: Alert[];
  worldWidth: number;
  worldHeight: number;
  selectedAssetId: string | null;
  onSelectAsset: (id: string | null) => void;
}

const STATUS_COLORS: Record<string, string> = {
  en_route: "#3b82f6", loitering: "#22c55e", rtb: "#f59e0b",
  idle: "#64748b", low_battery: "#f59e0b", critical: "#ef4444",
  offline: "#475569", mission_complete: "#22c55e", destroyed: "#dc2626",
};

const VEHICLE_ICONS = {
  quadrotor: (ctx: CanvasRenderingContext2D, x: number, y: number, heading: number, size: number, color: string, selected: boolean) => {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((heading * Math.PI) / 180);
    // Drone body - diamond shape
    ctx.fillStyle = selected ? "#ffffff" : color;
    ctx.beginPath();
    ctx.moveTo(0, -size * 1.2);
    ctx.lineTo(size * 0.7, 0);
    ctx.lineTo(0, size * 0.5);
    ctx.lineTo(-size * 0.7, 0);
    ctx.closePath();
    ctx.fill();
    // Center dot
    ctx.fillStyle = selected ? color : "#0a0e17";
    ctx.beginPath();
    ctx.arc(0, -size * 0.2, size * 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  },
  fixed_wing: (ctx: CanvasRenderingContext2D, x: number, y: number, heading: number, size: number, color: string, selected: boolean) => {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((heading * Math.PI) / 180);
    ctx.fillStyle = selected ? "#ffffff" : color;
    // Plane body
    ctx.beginPath();
    ctx.moveTo(0, -size * 1.3);
    ctx.lineTo(size * 0.3, -size * 0.2);
    ctx.lineTo(size * 1.0, size * 0.1);
    ctx.lineTo(size * 0.3, size * 0.3);
    ctx.lineTo(size * 0.15, size * 0.8);
    ctx.lineTo(size * 0.4, size * 1.0);
    ctx.lineTo(-size * 0.4, size * 1.0);
    ctx.lineTo(-size * 0.15, size * 0.8);
    ctx.lineTo(-size * 0.3, size * 0.3);
    ctx.lineTo(-size * 1.0, size * 0.1);
    ctx.lineTo(-size * 0.3, -size * 0.2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  },
  ground_rover: (ctx: CanvasRenderingContext2D, x: number, y: number, heading: number, size: number, color: string, selected: boolean) => {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((heading * Math.PI) / 180);
    ctx.fillStyle = selected ? "#ffffff" : color;
    // Rover body - rounded rectangle
    const w = size * 1.2;
    const h = size * 1.6;
    ctx.beginPath();
    ctx.roundRect(-w / 2, -h / 2, w, h, size * 0.25);
    ctx.fill();
    // Direction indicator
    ctx.fillStyle = selected ? color : "#0a0e17";
    ctx.beginPath();
    ctx.moveTo(0, -h / 2 + 2);
    ctx.lineTo(-size * 0.25, -h / 2 + size * 0.5);
    ctx.lineTo(size * 0.25, -h / 2 + size * 0.5);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  },
};

export function MapView({
  assets, alerts, worldWidth, worldHeight, selectedAssetId, onSelectAsset,
}: MapViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const assetsRef = useRef(assets);
  assetsRef.current = assets;

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current;
      const container = containerRef.current;
      if (!canvas || !container) return;
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const clickX = (e.clientX - rect.left) * dpr;
      const clickY = (e.clientY - rect.top) * dpr;
      const scaleX = (rect.width * dpr) / worldWidth;
      const scaleY = (rect.height * dpr) / worldHeight;
      let closest: string | null = null;
      let closestDist = 35 * dpr;
      for (const asset of assetsRef.current) {
        const ax = asset.position.x * scaleX;
        const ay = asset.position.y * scaleY;
        const dist = Math.sqrt((clickX - ax) ** 2 + (clickY - ay) ** 2);
        if (dist < closestDist) { closestDist = dist; closest = asset.id; }
      }
      onSelectAsset(closest === selectedAssetId ? null : closest);
    },
    [worldWidth, worldHeight, selectedAssetId, onSelectAsset]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const scaleX = w / worldWidth;
    const scaleY = h / worldHeight;
    const now = Date.now();

    // ── Background with subtle radial gradient ──
    const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w * 0.7);
    bgGrad.addColorStop(0, "#0d1520");
    bgGrad.addColorStop(1, "#060a10");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // ── Terrain texture (subtle noise-like dots) ──
    ctx.fillStyle = "#ffffff";
    ctx.globalAlpha = 0.015;
    for (let i = 0; i < 300; i++) {
      const tx = (Math.sin(i * 127.1 + 311.7) * 43758.5) % 1 * w;
      const ty = (Math.sin(i * 269.5 + 183.3) * 43758.5) % 1 * h;
      ctx.fillRect(Math.abs(tx), Math.abs(ty), 1, 1);
    }
    ctx.globalAlpha = 1;

    // ── Grid with graduated opacity ──
    for (let x = 0; x <= worldWidth; x += 100) {
      const px = x * scaleX;
      const isMajor = x % 200 === 0;
      ctx.strokeStyle = isMajor ? "#1a2540" : "#111c30";
      ctx.lineWidth = isMajor ? 0.8 : 0.4;
      ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, h); ctx.stroke();
    }
    for (let y = 0; y <= worldHeight; y += 100) {
      const py = y * scaleY;
      const isMajor = y % 200 === 0;
      ctx.strokeStyle = isMajor ? "#1a2540" : "#111c30";
      ctx.lineWidth = isMajor ? 0.8 : 0.4;
      ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(w, py); ctx.stroke();
    }

    // ── Grid coordinate labels ──
    ctx.font = "9px 'JetBrains Mono', monospace";
    ctx.fillStyle = "#263550";
    ctx.textAlign = "center";
    for (let x = 0; x <= worldWidth; x += 200) {
      ctx.fillText(`${x}`, x * scaleX, h - 4);
    }
    ctx.textAlign = "left";
    for (let y = 200; y <= worldHeight; y += 200) {
      ctx.fillText(`${y}`, 4, y * scaleY + 3);
    }

    // ── Base/home markers ──
    const homes = new Map<string, { x: number; y: number }>();
    for (const asset of assets) {
      // Approximate home from waypoint labeled HOME or from start of scenario
      const homeWp = asset.waypoints.find(wp => wp.label.toUpperCase().includes("HOME"));
      if (homeWp) {
        const key = `${homeWp.x},${homeWp.y}`;
        if (!homes.has(key)) homes.set(key, { x: homeWp.x, y: homeWp.y });
      }
    }
    for (const [, pos] of homes) {
      const hx = pos.x * scaleX;
      const hy = pos.y * scaleY;
      // Landing pad circles
      ctx.strokeStyle = "#22c55e30";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath(); ctx.arc(hx, hy, 12, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(hx, hy, 6, 0, Math.PI * 2); ctx.stroke();
      ctx.setLineDash([]);
      // H marker
      ctx.fillStyle = "#22c55e40";
      ctx.font = "bold 8px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText("H", hx, hy + 3);
    }

    // ── Draw each asset ─────────────────────
    for (const asset of assets) {
      const ax = asset.position.x * scaleX;
      const ay = asset.position.y * scaleY;
      const color = STATUS_COLORS[asset.status] ?? "#64748b";
      const isSelected = asset.id === selectedAssetId;

      // ── Radar/detection radius for selected asset ──
      if (isSelected) {
        const radarRadius = 50 * Math.min(scaleX, scaleY);
        const radarGrad = ctx.createRadialGradient(ax, ay, 0, ax, ay, radarRadius);
        radarGrad.addColorStop(0, `${color}15`);
        radarGrad.addColorStop(0.7, `${color}08`);
        radarGrad.addColorStop(1, `${color}00`);
        ctx.fillStyle = radarGrad;
        ctx.beginPath(); ctx.arc(ax, ay, radarRadius, 0, Math.PI * 2); ctx.fill();

        // Selection bracket corners
        const bSize = 18;
        const bOff = 22;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        // Top-left
        ctx.beginPath(); ctx.moveTo(ax - bOff, ay - bOff + bSize); ctx.lineTo(ax - bOff, ay - bOff); ctx.lineTo(ax - bOff + bSize, ay - bOff); ctx.stroke();
        // Top-right
        ctx.beginPath(); ctx.moveTo(ax + bOff - bSize, ay - bOff); ctx.lineTo(ax + bOff, ay - bOff); ctx.lineTo(ax + bOff, ay - bOff + bSize); ctx.stroke();
        // Bottom-left
        ctx.beginPath(); ctx.moveTo(ax - bOff, ay + bOff - bSize); ctx.lineTo(ax - bOff, ay + bOff); ctx.lineTo(ax - bOff + bSize, ay + bOff); ctx.stroke();
        // Bottom-right
        ctx.beginPath(); ctx.moveTo(ax + bOff - bSize, ay + bOff); ctx.lineTo(ax + bOff, ay + bOff); ctx.lineTo(ax + bOff, ay + bOff - bSize); ctx.stroke();
      }

      // ── Waypoint path ──
      if (asset.waypoints.length > 0) {
        // Route line
        ctx.strokeStyle = isSelected ? `${color}70` : `${color}25`;
        ctx.lineWidth = isSelected ? 1.5 : 0.8;
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        for (const wp of asset.waypoints) {
          ctx.lineTo(wp.x * scaleX, wp.y * scaleY);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // Waypoint markers
        for (let i = 0; i < asset.waypoints.length; i++) {
          const wp = asset.waypoints[i];
          const wpx = wp.x * scaleX;
          const wpy = wp.y * scaleY;

          // Diamond waypoint marker
          const wSize = isSelected ? 5 : 3;
          ctx.fillStyle = isSelected ? `${color}90` : `${color}40`;
          ctx.save();
          ctx.translate(wpx, wpy);
          ctx.rotate(Math.PI / 4);
          ctx.fillRect(-wSize / 2, -wSize / 2, wSize, wSize);
          ctx.restore();

          // Label for selected
          if (isSelected && wp.label) {
            ctx.fillStyle = "#94a3b8";
            ctx.font = "8px 'JetBrains Mono', monospace";
            ctx.textAlign = "center";
            ctx.fillText(wp.label, wpx, wpy - 8);
          }
        }
      }

      // ── Speed vector line ──
      if (asset.speed_mps > 1) {
        const headingRad = (asset.heading_deg * Math.PI) / 180;
        const vecLen = Math.min(30, asset.speed_mps * 1.5);
        const grad = ctx.createLinearGradient(ax, ay,
          ax + Math.sin(headingRad) * vecLen,
          ay - Math.cos(headingRad) * vecLen
        );
        grad.addColorStop(0, `${color}80`);
        grad.addColorStop(1, `${color}00`);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(
          ax + Math.sin(headingRad) * vecLen,
          ay - Math.cos(headingRad) * vecLen
        );
        ctx.stroke();
      }

      // ── Vehicle icon ──
      const iconSize = isSelected ? 9 : 7;
      const iconFn = VEHICLE_ICONS[asset.type as keyof typeof VEHICLE_ICONS] ?? VEHICLE_ICONS.quadrotor;
      iconFn(ctx, ax, ay, asset.heading_deg, iconSize, color, isSelected);

      // ── Callsign label ──
      ctx.font = `${isSelected ? "bold " : ""}10px 'JetBrains Mono', monospace`;
      ctx.textAlign = "center";
      // Label background
      const labelText = asset.callsign;
      const labelWidth = ctx.measureText(labelText).width + 8;
      ctx.fillStyle = "#0a0e17cc";
      ctx.fillRect(ax - labelWidth / 2, ay + 12, labelWidth, 14);
      // Label text
      ctx.fillStyle = isSelected ? "#ffffff" : "#cbd5e1";
      ctx.fillText(labelText, ax, ay + 23);

      // ── Battery bar ──
      const barWidth = 28;
      const barHeight = 2.5;
      const barX = ax - barWidth / 2;
      const barY = ay + 27;
      ctx.fillStyle = "#1a223466";
      ctx.fillRect(barX, barY, barWidth, barHeight);
      const batteryColor =
        asset.battery_pct > 50 ? "#22c55e" :
        asset.battery_pct > 20 ? "#f59e0b" : "#ef4444";
      ctx.fillStyle = batteryColor;
      ctx.fillRect(barX, barY, barWidth * (asset.battery_pct / 100), barHeight);

      // ── Warning pulse for critical assets ──
      if (asset.status === "critical" || asset.status === "low_battery") {
        const pulsePhase = (Math.sin(now / 400) + 1) / 2;
        ctx.strokeStyle = `rgba(239, 68, 68, ${0.15 + pulsePhase * 0.4})`;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.arc(ax, ay, 16 + pulsePhase * 4, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // ── HUD overlay — compass rose (top-center) ──
    const cx = w / 2;
    ctx.fillStyle = "#263550";
    ctx.font = "bold 9px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText("N", cx, 14);

    // ── Scale bar (bottom-left) ──
    const scaleBarMeters = 100;
    const scaleBarPx = scaleBarMeters * scaleX;
    ctx.fillStyle = "#334155";
    ctx.fillRect(14, h - 14, scaleBarPx, 1.5);
    ctx.fillRect(14, h - 18, 1, 5);
    ctx.fillRect(14 + scaleBarPx, h - 18, 1, 5);
    ctx.font = "9px 'JetBrains Mono', monospace";
    ctx.textAlign = "left";
    ctx.fillText(`${scaleBarMeters}m`, 14, h - 22);

    // ── World size (top-right) ──
    ctx.fillStyle = "#263550";
    ctx.font = "9px 'JetBrains Mono', monospace";
    ctx.textAlign = "right";
    ctx.fillText(`${worldWidth} × ${worldHeight}m`, w - 8, 14);

    // ── Active alert count badge ──
    const activeAlerts = alerts.filter(a => !a.acknowledged).length;
    if (activeAlerts > 0) {
      const badgeX = 14;
      const badgeY = 14;
      ctx.fillStyle = "#ef444430";
      ctx.beginPath();
      ctx.roundRect(badgeX, badgeY, 70, 18, 4);
      ctx.fill();
      ctx.fillStyle = "#ef4444";
      ctx.font = "bold 9px 'JetBrains Mono', monospace";
      ctx.textAlign = "left";
      ctx.fillText(`⚠ ${activeAlerts} ALERT${activeAlerts > 1 ? "S" : ""}`, badgeX + 6, badgeY + 13);
    }

  }, [assets, alerts, worldWidth, worldHeight, selectedAssetId]);

  return (
    <div ref={containerRef} className="w-full h-full relative">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 cursor-crosshair"
        onClick={handleClick}
      />
      {assets.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-aegis-text-muted text-sm font-mono tracking-widest mb-2">AWAITING TELEMETRY</div>
            <div className="w-8 h-0.5 bg-aegis-accent/30 mx-auto animate-pulse" />
          </div>
        </div>
      )}
    </div>
  );
}
