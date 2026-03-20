# AEGIS — Safety & Threat Model

## Core Safety Principle

The AI agent (OpenClaw) is an advisor, not an authority.
It may recommend, summarize, and prepare actions — but the operator
and the policy engine are the only entities that authorize execution.

## Action Risk Classification

| Level    | Description                       | Gate              | Example                         |
|----------|-----------------------------------|-------------------|---------------------------------|
| Low      | Informational, read-only          | Auto-execute      | "What is HAWK-1's battery?"     |
| Medium   | State change, reversible          | Log + confirm     | "Reroute HAWK-2 to waypoint B3" |
| High     | Irreversible or safety-critical   | Operator approval | "Return all assets to base"     |
| Blocked  | Violates safety invariants        | Reject outright   | "Disable battery monitoring"    |

## Threat Vectors

### 1. Prompt Injection via Operator Console
- **Threat:** Operator input crafted to manipulate the AI agent
- **Mitigation:** System prompt instructs agent to only use defined tools.
  All tool calls are validated by the policy engine before execution.
  Agent output is never executed as code.

### 2. Unsafe Command Escalation
- **Threat:** Operator issues dangerous commands (destroy assets, ignore alerts)
- **Mitigation:** Policy engine deny-list for destructive operations.
  High-risk commands require explicit approval modal.
  All commands logged with full context.

### 3. Stale Telemetry
- **Threat:** Decisions made on outdated sensor data
- **Mitigation:** Every telemetry frame includes a timestamp.
  Frontend shows data age indicator. Policy engine rejects actions
  if telemetry is older than a configurable threshold.

### 4. Agent Hallucination
- **Threat:** AI agent fabricates asset state or invents capabilities
- **Mitigation:** Agent tools only read from the simulation state store.
  Agent cannot fabricate data — it can only format what the tools return.
  All tool calls and responses are logged.

### 5. Simulation Kill Switch
- **Threat:** Runaway simulation or agent loop
- **Mitigation:** Emergency stop endpoint (POST /api/simulation/stop).
  Frontend panic button. Rate limiting on command submissions.
  Maximum tool calls per command (configurable, default: 5).

## Policy Engine Rules (Phase 4)

```
ALLOW: query_*, get_*, list_*, summary_*        → auto-execute (low risk)
CONFIRM: assign_waypoints, reroute, set_speed    → log + execute (medium risk)
APPROVE: rtb_all, abort_mission, emergency_land  → operator approval (high risk)
BLOCK: disable_*, destroy_*, override_safety_*   → reject (blocked)
```

## Audit Trail Requirements

Every entry in the audit log must contain:
- Timestamp (UTC, millisecond precision)
- Event type (command, approval, rejection, alert, tool call, etc.)
- Source (operator, agent, policy engine, simulation)
- Mission and asset context (if applicable)
- Human-readable message
- Machine-readable details (JSON)

The audit log is append-only. No deletions. No updates.

## Fail-Safe Behaviors

| Condition              | System Response                              |
|------------------------|----------------------------------------------|
| Agent unreachable      | Commands queue; operator notified             |
| Database unreachable   | Simulation continues; commands rejected       |
| WebSocket disconnect   | Frontend shows DISCONNECTED; auto-reconnect   |
| Battery critical (<5%) | Auto-RTB triggered; operator alerted          |
| Comms loss simulated   | Asset marked OFFLINE; operator alerted        |
