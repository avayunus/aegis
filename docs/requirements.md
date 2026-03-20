# AEGIS — Requirements Document

## Functional Requirements

### FR-1: Mission Management
- FR-1.1: System shall support creating, starting, and completing missions
- FR-1.2: Each mission has a type (SAR, patrol, recon), asset list, and waypoint plan
- FR-1.3: Mission state shall be persisted to the database

### FR-2: Asset Simulation
- FR-2.1: System shall simulate autonomous vehicles in a 2D world
- FR-2.2: Vehicles navigate waypoint queues with heading, speed, and battery
- FR-2.3: Battery drains proportionally to movement and time
- FR-2.4: Vehicles transition through defined status states (idle, en_route, rtb, etc.)

### FR-3: Real-Time Telemetry
- FR-3.1: Simulation state shall be broadcast via WebSocket at configurable tick rate
- FR-3.2: Each frame includes all asset positions, statuses, alerts, and mission summary
- FR-3.3: Frontend shall render updates within one frame of receipt

### FR-4: Operator Commands
- FR-4.1: Operator shall type natural-language commands in a console
- FR-4.2: Commands are interpreted by the AI agent (OpenClaw)
- FR-4.3: Every command receives a structured response with actions taken

### FR-5: Safety Guardrails
- FR-5.1: Every action shall be classified by risk level (low/medium/high/blocked)
- FR-5.2: High-risk actions require explicit operator approval
- FR-5.3: Blocked actions are rejected and logged

### FR-6: Audit Trail
- FR-6.1: Every command, action, approval, rejection, and alert shall be logged
- FR-6.2: Audit log is append-only (no updates, no deletes)
- FR-6.3: Each entry includes timestamp, source, event type, and context

### FR-7: Anomaly Detection
- FR-7.1: System shall detect low battery, route deviation, and asset conflicts
- FR-7.2: Alerts are surfaced in real-time in the operator UI

## Non-Functional Requirements

### NFR-1: Performance
- Simulation shall maintain 2 Hz tick rate with up to 20 assets
- WebSocket latency shall be under 100ms on localhost
- Frontend shall render at 30+ FPS

### NFR-2: Reliability
- Backend shall recover gracefully from WebSocket disconnects
- Frontend shall auto-reconnect with exponential backoff
- Database writes shall not block the simulation loop

### NFR-3: Security
- All API endpoints validate input via Pydantic models
- Agent tool calls are sandboxed to defined tool list
- No raw SQL or shell execution from operator input

### NFR-4: Usability
- UI shall be usable at 1920x1080 resolution minimum
- All panels visible simultaneously without scrolling the layout
- Status changes visible within 1 second of occurrence

### NFR-5: Maintainability
- Code organized in clear module boundaries
- Type hints on all Python functions
- TypeScript strict mode enabled
- Automated test suite with >70% coverage target
