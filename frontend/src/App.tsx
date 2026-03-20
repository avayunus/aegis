import { useWebSocket } from "./hooks/useWebSocket";
import { MapView } from "./components/MapView";
import { AssetPanel } from "./components/AssetPanel";
import { AlertFeed } from "./components/AlertFeed";
import { CommandConsole } from "./components/CommandConsole";
import { SystemHealth } from "./components/SystemHealth";
import { TelemetryPanel } from "./components/TelemetryPanel";

/**
 * Root application layout — mission control console.
 *
 * The layout uses a dense, multi-panel grid reminiscent of real
 * ground control stations. The tactical map dominates the center,
 * with panels for assets, telemetry, alerts, and the command console
 * arranged around it.
 */
export default function App() {
  const WS_URL = `ws://${window.location.hostname}:8000/api/telemetry/ws`;
  const { frame, status } = useWebSocket(WS_URL);

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-aegis-bg">
      {/* ── Top bar ────────────────────────────────── */}
      <header className="flex items-center justify-between px-4 py-2 border-b border-aegis-border bg-aegis-surface">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold tracking-widest uppercase text-aegis-accent">
            AEGIS
          </h1>
          <span className="text-xs text-aegis-text-muted font-mono">
            Mission Control v0.1
          </span>
        </div>
        <div className="flex items-center gap-4">
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
            <span className="text-xs text-aegis-text-muted font-mono">
              T+{frame.tick}
            </span>
          )}
        </div>
      </header>

      {/* ── Main grid ──────────────────────────────── */}
      <div className="flex-1 grid grid-cols-[280px_1fr_300px] grid-rows-[1fr_220px] gap-px overflow-hidden">
        {/* Left column: asset list */}
        <div className="row-span-2 overflow-y-auto border-r border-aegis-border bg-aegis-surface">
          <AssetPanel assets={frame?.assets ?? []} />
        </div>

        {/* Center top: tactical map */}
        <div className="overflow-hidden bg-aegis-bg">
          <MapView
            assets={frame?.assets ?? []}
            worldWidth={frame?.world.width ?? 1000}
            worldHeight={frame?.world.height ?? 1000}
          />
        </div>

        {/* Right column top: telemetry + system health */}
        <div className="overflow-y-auto border-l border-aegis-border bg-aegis-surface">
          <SystemHealth mission={frame?.mission ?? null} status={status} />
          <TelemetryPanel assets={frame?.assets ?? []} />
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
