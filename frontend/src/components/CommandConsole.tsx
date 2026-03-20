import { useState, useRef, useEffect } from "react";
import { Send, ChevronRight, ShieldAlert, Check, X } from "lucide-react";
import { submitCommand, approveCommand, rejectCommand } from "../services/api";
import type { CommandResponse } from "../services/api";

interface LogEntry {
  id: number;
  type: "operator" | "system" | "error" | "approval" | "blocked";
  text: string;
  timestamp: string;
  commandId?: string;
  riskLevel?: string;
}

/**
 * Operator command console — the natural-language interface.
 *
 * Phase 1: Commands are interpreted by pattern matching and executed
 * against the live simulation. High-risk commands show approval buttons.
 */
export function CommandConsole() {
  const [input, setInput] = useState("");
  const [log, setLog] = useState<LogEntry[]>([
    {
      id: 0,
      type: "system",
      text: "AEGIS operator console ready. Try: 'status of HAWK-1', 'return HAWK-2 to base', 'battery report', 'mission summary'",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const idCounter = useRef(1);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  const addEntry = (
    type: LogEntry["type"],
    text: string,
    commandId?: string,
    riskLevel?: string
  ) => {
    setLog((prev) => [
      ...prev,
      {
        id: idCounter.current++,
        type,
        text,
        timestamp: new Date().toLocaleTimeString(),
        commandId,
        riskLevel,
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
      const result: CommandResponse = await submitCommand(trimmed);

      if (result.status === "blocked") {
        addEntry(
          "blocked",
          `BLOCKED: ${result.interpreted_intent}. Command denied by policy engine.`,
          result.command_id,
          result.risk_level
        );
      } else if (result.requires_approval) {
        addEntry(
          "approval",
          result.ai_response
            ? `${result.ai_response}`
            : `⚠ HIGH RISK: "${result.interpreted_intent}" — requires operator approval`,
          result.command_id,
          result.risk_level
        );
      } else {
        // Build the display text
        const aiText = result.ai_response || "";
        const summary = result.result_summary || result.interpreted_intent;
        const displayText = aiText || summary;
        const prefix = result.risk_level === "medium" ? "[CONFIRM] " : "";
        addEntry("system", prefix + displayText, result.command_id, result.risk_level);
      }
    } catch (err) {
      addEntry("error", `Failed to send command: ${err}`);
    } finally {
      setIsProcessing(false);
      inputRef.current?.focus();
    }
  };

  const handleApprove = async (commandId: string) => {
    try {
      const result = await approveCommand(commandId);
      const summary = (result as Record<string, string>).result_summary ?? "Approved and executed";
      addEntry("system", `✓ APPROVED: ${summary}`, commandId);
      // Remove the approval entry
      setLog((prev) =>
        prev.map((e) =>
          e.commandId === commandId && e.type === "approval"
            ? { ...e, type: "system" as const, text: `✓ APPROVED: ${summary}` }
            : e
        )
      );
    } catch (err) {
      addEntry("error", `Approval failed: ${err}`);
    }
  };

  const handleReject = async (commandId: string) => {
    try {
      await rejectCommand(commandId);
      setLog((prev) =>
        prev.map((e) =>
          e.commandId === commandId && e.type === "approval"
            ? { ...e, type: "system" as const, text: "✗ REJECTED by operator" }
            : e
        )
      );
    } catch (err) {
      addEntry("error", `Rejection failed: ${err}`);
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
                <span className="text-aegis-success flex-shrink-0">SYS</span>
                <span className="text-aegis-text-dim">{entry.text}</span>
              </>
            )}

            {entry.type === "error" && (
              <>
                <span className="text-aegis-danger flex-shrink-0">ERR</span>
                <span className="text-aegis-danger">{entry.text}</span>
              </>
            )}

            {entry.type === "blocked" && (
              <>
                <ShieldAlert className="w-3 h-3 text-aegis-danger mt-0.5 flex-shrink-0" />
                <span className="text-aegis-danger">{entry.text}</span>
              </>
            )}

            {entry.type === "approval" && (
              <div className="flex items-center gap-2 flex-1">
                <ShieldAlert className="w-3 h-3 text-aegis-warning mt-0.5 flex-shrink-0" />
                <span className="text-aegis-warning flex-1">{entry.text}</span>
                <button
                  onClick={() => entry.commandId && handleApprove(entry.commandId)}
                  className="px-2 py-0.5 bg-aegis-success/20 text-aegis-success rounded text-[10px] font-semibold hover:bg-aegis-success/30 flex items-center gap-1"
                >
                  <Check className="w-3 h-3" /> APPROVE
                </button>
                <button
                  onClick={() => entry.commandId && handleReject(entry.commandId)}
                  className="px-2 py-0.5 bg-aegis-danger/20 text-aegis-danger rounded text-[10px] font-semibold hover:bg-aegis-danger/30 flex items-center gap-1"
                >
                  <X className="w-3 h-3" /> REJECT
                </button>
              </div>
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
