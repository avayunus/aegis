import { useState, useRef, useEffect } from "react";
import { Send, ChevronRight } from "lucide-react";
import { submitCommand } from "../services/api";

interface LogEntry {
  id: number;
  type: "operator" | "system" | "error";
  text: string;
  timestamp: string;
}

/**
 * Operator command console — the natural-language interface.
 *
 * Operators type commands here. The AI (via OpenClaw in Phase 3) interprets
 * and executes them. For now, commands are echoed and sent to the backend stub.
 */
export function CommandConsole() {
  const [input, setInput] = useState("");
  const [log, setLog] = useState<LogEntry[]>([
    {
      id: 0,
      type: "system",
      text: "AEGIS operator console initialized. Type a command or query.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const idCounter = useRef(1);

  // Auto-scroll to bottom when new log entries appear
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  const addEntry = (type: LogEntry["type"], text: string) => {
    setLog((prev) => [
      ...prev,
      {
        id: idCounter.current++,
        type,
        text,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const handleSubmit = async () => {
    const trimmed = input.trim();
    if (!trimmed || isProcessing) return;

    addEntry("operator", trimmed);
    setInput("");
    setIsProcessing(true);

    try {
      const result = await submitCommand(trimmed);
      const summary =
        (result as Record<string, string>).result_summary ??
        (result as Record<string, string>).status ??
        "Command received.";
      addEntry("system", String(summary));
    } catch (err) {
      addEntry("error", `Failed to send command: ${err}`);
    } finally {
      setIsProcessing(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="panel-header">Operator Console</div>

      {/* Log output */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 font-mono text-xs">
        {log.map((entry) => (
          <div key={entry.id} className="flex gap-2">
            <span className="text-aegis-text-muted flex-shrink-0">
              {entry.timestamp}
            </span>
            {entry.type === "operator" && (
              <>
                <ChevronRight className="w-3 h-3 text-aegis-accent mt-0.5 flex-shrink-0" />
                <span className="text-aegis-accent">{entry.text}</span>
              </>
            )}
            {entry.type === "system" && (
              <>
                <span className="text-aegis-text-muted flex-shrink-0">SYS</span>
                <span className="text-aegis-text-dim">{entry.text}</span>
              </>
            )}
            {entry.type === "error" && (
              <>
                <span className="text-aegis-danger flex-shrink-0">ERR</span>
                <span className="text-aegis-danger">{entry.text}</span>
              </>
            )}
          </div>
        ))}
        <div ref={logEndRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-aegis-border px-3 py-2 flex items-center gap-2">
        <ChevronRight className="w-4 h-4 text-aegis-accent flex-shrink-0" />
        <input
          ref={inputRef}
          type="text"
          className="flex-1 bg-transparent text-sm font-mono text-aegis-text placeholder:text-aegis-text-muted outline-none"
          placeholder={isProcessing ? "Processing..." : "Enter command..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isProcessing}
        />
        <button
          onClick={handleSubmit}
          disabled={isProcessing || !input.trim()}
          className="p-1.5 rounded hover:bg-aegis-accent/20 disabled:opacity-30 transition-colors"
        >
          <Send className="w-4 h-4 text-aegis-accent" />
        </button>
      </div>
    </div>
  );
}
