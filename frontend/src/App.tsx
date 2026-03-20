import { useState } from "react";
import { useWebSocket } from "./hooks/useWebSocket";
import { MapView } from "./components/MapView";
import { AssetPanel } from "./components/AssetPanel";
import { AlertFeed } from "./components/AlertFeed";
import { CommandConsole } from "./components/CommandConsole";
import { SystemHealth } from "./components/SystemHealth";
import { TelemetryPanel } from "./components/TelemetryPanel";
import { ControlBar } from "./components/ControlBar";

/**
 * Root application layout — mission control console.
 *
 * Phase 2: Added asset selection, control bar with pause/resume/reset/scenario,
 * and wired selection state across map + asset panel + telemetry.
 */
export default function App() {
  const WS_URL = `ws://${window.location.hostname}:8000/api/telemetry/ws`;
  const { frame, status } = useWebSocket(WS_URL);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);

  const selectedAsset = frame?.assets.find((a) => a.id === selectedAssetId) ?? null;

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-aegis-bg">
      {/* ── Top bar ────────────────────────────────── */}
      <header className="flex items-center justify-between px-4 py-2 border-b border-aegis-border bg-aegis-surface">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold tracking-widest uppercase text-aegis-accent">
            AEGIS
          </h1>
          <span className="text-xs text-aegis-text-muted font-mono">
            {frame?.mission_name || "Mission Control"}
          </span>
          {frame?.paused && (
            <span className="text-[10px] font-mono font-bold bg-aegis-warning/20 text-aegis-warning px-2 py-0.5 rounded animate-pulse">
              PAUSED
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <ControlBar paused={frame?.paused ?? false} />
          <div className="w-px h-5 bg-aegis-border" />
          {frame && (
            <span className="text-xs text-aegis-text-muted font-mono">
              {Math.floor(frame.elapsed_seconds / 60).toString().padStart(2, "0")}:
              {Math.floor(frame.elapsed_seconds % 60).toString().padStart(2, "0")}
            </span>
          )}
          <div className="flex items-center gap-2 text-xs">
            <span
              className={`status-dot ${
                status === "connected"
                  ? "status-dot-active"
                  : status === "connecting"
                  ? "status-dot-warning"
                  : "status-dot-danger"
              }`}
            />
            <span className="text-aegis-text-dim font-mono uppercase">
              {status}
            </span>
          </div>
          {frame && (
            <span className="text-[10px] text-aegis-text-muted font-mono bg-aegis-bg/50 px-1.5 py-0.5 rounded">
              T+{frame.tick}
            </span>
          )}
        </div>
      </header>

      {/* ── Main grid ──────────────────────────────── */}
      <div className="flex-1 grid grid-cols-[280px_1fr_300px] grid-rows-[1fr_220px] gap-px overflow-hidden">
        {/* Left column: asset list */}
        <div className="row-span-2 overflow-y-auto border-r border-aegis-border bg-aegis-surface">
          <AssetPanel
            assets={frame?.assets ?? []}
            selectedId={selectedAssetId}
            onSelect={setSelectedAssetId}
          />
        </div>

        {/* Center top: tactical map */}
        <div className="overflow-hidden bg-aegis-bg">
          <MapView
            assets={frame?.assets ?? []}
            alerts={frame?.alerts ?? []}
            worldWidth={frame?.world.width ?? 1000}
            worldHeight={frame?.world.height ?? 1000}
            selectedAssetId={selectedAssetId}
            onSelectAsset={setSelectedAssetId}
          />
        </div>

        {/* Right column top: telemetry + system health */}
        <div className="overflow-y-auto border-l border-aegis-border bg-aegis-surface">
          <SystemHealth mission={frame?.mission ?? null} status={status} />
          <TelemetryPanel
            assets={frame?.assets ?? []}
            selectedId={selectedAssetId}
            onSelect={setSelectedAssetId}
          />
        </div>

        {/* Center bottom: command console */}
        <div className="border-t border-aegis-border bg-aegis-surface">
          <CommandConsole />
        </div>

        {/* Right bottom: alert feed */}
        <div className="border-t border-l border-aegis-border bg-aegis-surface overflow-y-auto">
          <AlertFeed alerts={frame?.alerts ?? []} />
        </div>
      </div>
    </div>
  );
}
