# AEGIS — System Architecture

## Overview

AEGIS is a mission-control platform where a human operator supervises
simulated autonomous assets (drones, rovers) through a tactical console.
An AI agent interprets natural-language commands, but all actions flow
through a policy engine that enforces safety boundaries.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      OPERATOR CONSOLE (React)                     │
│  ┌──────────┐ ┌────────┐ ┌──────┐ ┌──────────┐ ┌───────────┐   │
│  │ Tactical  │ │ Asset  │ │Alert │ │ Command  │ │ Telemetry │   │
│  │ Map       │ │ Panel  │ │Feed  │ │ Console  │ │ Readout   │   │
│  └──────────┘ └────────┘ └──────┘ └──────────┘ └───────────┘   │
└───────────────────────┬──────────────────────────────────────────┘
                        │
              WebSocket (telemetry)  +  REST (commands, queries)
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                     BACKEND (FastAPI, Python)                      │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    API LAYER                                │   │
│  │  /health  /missions  /assets  /commands  /telemetry/ws     │   │
│  └─────────────┬──────────────────────────────────────────────┘   │
│                │                                                    │
│  ┌─────────────▼──────────┐   ┌───────────────────────────────┐   │
│  │   COMMAND ROUTER        │   │   TELEMETRY BROADCASTER      │   │
│  │   Receives NL text,     │   │   Pushes sim state to all    │   │
│  │   routes to AI agent    │   │   connected WebSocket clients│   │
│  └─────────────┬──────────┘   └───────────────┬───────────────┘   │
│                │                               │                    │
│  ┌─────────────▼──────────┐   ┌───────────────▼───────────────┐   │
│  │   POLICY ENGINE         │   │   SIMULATION ENGINE           │   │
│  │   Risk classification   │   │   2D world with vehicles,    │   │
│  │   Approval gating       │   │   waypoints, battery, physics│   │
│  │   Allow/deny rules      │   │   Runs at 2 Hz tick rate     │   │
│  └─────────────┬──────────┘   └───────────────────────────────┘   │
│                │                                                    │
│  ┌─────────────▼──────────┐   ┌───────────────────────────────┐   │
│  │   OPENCLAW AGENT        │   │   EVENT / ANOMALY ENGINE      │   │
│  │   NL interpretation     │   │   Low battery detection       │   │
│  │   Tool selection        │   │   Route deviation             │   │
│  │   Action orchestration  │   │   Comms loss                  │   │
│  └────────────────────────┘   └───────────────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    DATA LAYER                               │   │
│  │   SQLite (MVP) → PostgreSQL                                 │   │
│  │   missions | assets | commands | audit_log                  │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Operator Console (Frontend)
- React + TypeScript + Vite + Tailwind
- Connects via WebSocket for real-time telemetry at 2 Hz
- REST calls for commands, queries, approvals
- Canvas-based tactical map rendering
- No business logic — pure presentation layer

### API Layer
- FastAPI with automatic OpenAPI docs at /docs
- REST endpoints for CRUD operations
- WebSocket endpoint for telemetry streaming
- Pydantic models for request/response validation

### Command Router
- Receives natural-language text from operator
- Sends to OpenClaw agent for interpretation (Phase 3)
- Routes through policy engine for risk classification (Phase 4)
- Returns structured response with actions taken

### Policy Engine (Phase 4)
- Classifies every action as low/medium/high/blocked risk
- Low: auto-execute
- Medium: execute with confirmation log
- High: require operator approval
- Blocked: reject outright (e.g., "destroy all assets")
- All decisions logged to audit trail

### OpenClaw Agent (Phase 3)
- Interprets operator natural language into structured intent
- Selects appropriate tools (query status, assign waypoints, etc.)
- Generates summaries and reports
- Never executes directly — always through policy gate

### Simulation Engine
- Discrete-time 2D simulator running in asyncio background task
- Vehicles navigate waypoint queues with simple physics
- Battery drains proportional to movement
- Alert generation for anomalies (low battery, completion, etc.)
- State broadcast every tick to all WebSocket clients

### Event / Anomaly Engine (Phase 6)
- Monitors telemetry stream for anomalous conditions
- Generates alerts surfaced in the operator console
- Feeds into OpenClaw for AI-generated recommendations

### Data Layer
- SQLAlchemy 2.0 async ORM
- SQLite for MVP (zero-config), PostgreSQL for production
- Four core tables: missions, assets, commands, audit_log
- Append-only audit log for full traceability

## Data Flow

1. Simulation engine ticks at 2 Hz
2. Each tick: vehicles move, battery drains, anomalies checked
3. Full world state serialized and broadcast via WebSocket
4. Frontend renders new frame on each message
5. Operator types command → POST /api/commands
6. Backend routes through policy → agent → execution
7. Result logged to audit trail and returned to frontend

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Simulator | Custom 2D Python | Full control, no external deps, reliable demos |
| Frontend framework | React + Canvas | Fast rendering, wide ecosystem, recruiter-friendly |
| Backend framework | FastAPI | Async, WebSocket native, auto-docs, Python AI ecosystem |
| Database | SQLite → PostgreSQL | Zero-config MVP, easy migration path |
| Real-time transport | WebSocket | Low latency, bidirectional, built into FastAPI |
| AI agent | OpenClaw | Open-source, tool-call architecture, auditable |
| Monorepo | Yes | Single clone, shared types, easier CI |
