# AEGIS

**Autonomous Engine for Guided Intelligence & Supervision**

A mission-control platform for simulated autonomous assets (drones, rovers, mixed fleets) where a human operator issues natural-language commands, observes real-time mission state, reviews AI-generated summaries, and safely supervises all system actions through explicit guardrails and auditability.

---

## What This Is

AEGIS simulates a fleet of autonomous vehicles executing missions (search-and-rescue, perimeter patrol, anomaly investigation) while a human operator supervises through a tactical console. An AI agent (powered by OpenClaw) interprets operator commands, orchestrates tools, and generates recommendations — but **never acts autonomously on high-risk decisions** without operator approval.

Every action is logged. Every decision is explainable. Every command is auditable.

## Key Capabilities

- **Tactical Map** — Real-time 2D visualization of all assets, waypoints, routes, and anomalies
- **Natural-Language Command Console** — Operator types plain English; the AI interprets and executes
- **Safety-First Action Model** — Low-risk actions auto-execute; high-risk actions require operator approval
- **Anomaly Detection Engine** — Detects low battery, route deviation, sensor failures, communication loss
- **Mission Replay** — Full temporal replay of any mission with decision audit trail
- **Post-Mission Reports** — AI-generated mission summaries with key events and recommendations

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    OPERATOR CONSOLE                       │
│  Tactical Map │ Assets │ Alerts │ Command │ Timeline      │
└──────────────┬───────────────────────────────────────────┘
               │ WebSocket + REST
┌──────────────▼───────────────────────────────────────────┐
│                    BACKEND (FastAPI)                       │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐  │
│  │ Command  │ │ Mission  │ │Telemetry│ │  Event /     │  │
│  │ Router   │ │ Service  │ │ Ingest  │ │  Anomaly Eng │  │
│  └────┬─────┘ └──────────┘ └─────────┘ └──────────────┘  │
│       │                                                    │
│  ┌────▼─────────────────────────────────────────────┐     │
│  │              POLICY ENGINE                        │     │
│  │  Risk Classification → Approval Gate → Audit Log  │     │
│  └────┬─────────────────────────────────────────────┘     │
│       │                                                    │
│  ┌────▼─────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  OpenClaw     │  │  Simulation    │  │  SQLite DB   │  │
│  │  Agent Layer  │  │  Engine (2D)   │  │  (missions,  │  │
│  │  (NL → Tools) │  │  (physics,     │  │   assets,    │  │
│  │               │  │   vehicles)    │  │   audit)     │  │
│  └───────────────┘  └────────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Frontend     | React, TypeScript, Vite, Tailwind |
| Backend      | Python, FastAPI, WebSockets       |
| Database     | SQLite (MVP) → PostgreSQL         |
| AI Agent     | OpenClaw Gateway + Custom Tools   |
| Simulation   | Custom 2D tactical engine (Python)|
| Deployment   | Docker, Docker Compose            |

## Quick Start

```bash
# Clone
git clone git@github.com:YOUR_USERNAME/aegis.git
cd aegis

# Setup everything
make setup

# Start backend
make backend

# Start frontend (new terminal)
make frontend
```

## Project Structure

```
aegis/
├── backend/          # FastAPI service + simulation engine
├── frontend/         # React operator console
├── docs/             # Architecture, requirements, safety model
├── scenarios/        # Demo mission configurations
├── scripts/          # Setup and demo scripts
└── infra/            # Docker and deployment configs
```

## Development Phases

- [x] Phase 0: Project skeleton and environment
- [ ] Phase 1: Simulation engine (2D tactical world)
- [ ] Phase 2: Operator UI (tactical map, panels)
- [ ] Phase 3: OpenClaw agent integration
- [ ] Phase 4: Safety guardrails and policy engine
- [ ] Phase 5: Replay, reports, anomaly engine
- [ ] Phase 6: Testing hardening and demo polish

## License

MIT
