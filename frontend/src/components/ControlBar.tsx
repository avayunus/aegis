import { useState, useEffect } from "react";
import { Pause, Play, RotateCcw, Map } from "lucide-react";
import {
  pauseSimulation,
  resumeSimulation,
  resetSimulation,
  loadScenario,
} from "../services/api";

interface ControlBarProps {
  paused: boolean;
}

interface ScenarioMeta {
  id: string;
  name: string;
  filename: string;
  asset_count: number;
}

/**
 * Simulation control buttons — pause, resume, reset, scenario selector.
 * Lives in the header bar.
 */
export function ControlBar({ paused }: ControlBarProps) {
  const [scenarios, setScenarios] = useState<ScenarioMeta[]>([]);
  const [showScenarios, setShowScenarios] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/missions/")
      .then((r) => r.json())
      .then((data) => {
        if (data.available_scenarios) {
          setScenarios(data.available_scenarios);
        }
      })
      .catch(() => {});
  }, []);

  const handlePauseResume = async () => {
    setLoading(true);
    try {
      if (paused) {
        await resumeSimulation();
      } else {
        await pauseSimulation();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await resetSimulation();
    } finally {
      setLoading(false);
    }
  };

  const handleLoadScenario = async (filename: string) => {
    setLoading(true);
    setShowScenarios(false);
    try {
      await loadScenario(filename);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-1.5 relative">
      {/* Pause / Resume */}
      <button
        onClick={handlePauseResume}
        disabled={loading}
        className="flex items-center gap-1 px-2 py-1 text-[10px] font-mono font-semibold rounded
          border border-aegis-border hover:border-aegis-accent/50 hover:bg-aegis-accent/10
          disabled:opacity-40 transition-colors"
        title={paused ? "Resume simulation" : "Pause simulation"}
      >
        {paused ? (
          <>
            <Play className="w-3 h-3 text-aegis-success" />
            <span className="text-aegis-success">RESUME</span>
          </>
        ) : (
          <>
            <Pause className="w-3 h-3 text-aegis-warning" />
            <span className="text-aegis-text-dim">PAUSE</span>
          </>
        )}
      </button>

      {/* Reset */}
      <button
        onClick={handleReset}
        disabled={loading}
        className="flex items-center gap-1 px-2 py-1 text-[10px] font-mono font-semibold rounded
          border border-aegis-border hover:border-aegis-accent/50 hover:bg-aegis-accent/10
          disabled:opacity-40 transition-colors text-aegis-text-dim"
        title="Reset simulation"
      >
        <RotateCcw className="w-3 h-3" />
        RESET
      </button>

      {/* Scenario switcher */}
      <div className="relative">
        <button
          onClick={() => setShowScenarios(!showScenarios)}
          disabled={loading}
          className="flex items-center gap-1 px-2 py-1 text-[10px] font-mono font-semibold rounded
            border border-aegis-border hover:border-aegis-accent/50 hover:bg-aegis-accent/10
            disabled:opacity-40 transition-colors text-aegis-text-dim"
          title="Load scenario"
        >
          <Map className="w-3 h-3" />
          SCENARIO
        </button>

        {showScenarios && scenarios.length > 0 && (
          <div className="absolute top-full right-0 mt-1 bg-aegis-panel border border-aegis-border rounded-lg shadow-xl z-50 min-w-[240px]">
            <div className="px-3 py-2 border-b border-aegis-border text-[10px] font-mono text-aegis-text-muted uppercase tracking-wider">
              Load Scenario
            </div>
            {scenarios.map((s) => (
              <button
                key={s.id}
                onClick={() => handleLoadScenario(s.filename)}
                className="w-full px-3 py-2 text-left hover:bg-aegis-accent/10 transition-colors border-b border-aegis-border/50 last:border-0"
              >
                <div className="text-xs font-mono font-semibold text-aegis-text">
                  {s.name}
                </div>
                <div className="text-[10px] font-mono text-aegis-text-muted mt-0.5">
                  {s.asset_count} assets
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
