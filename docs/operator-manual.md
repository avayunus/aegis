# AEGIS — Operator Manual

## Starting a Mission

1. Launch the backend: `make backend`
2. Launch the frontend: `make frontend`
3. Open http://localhost:5173 in your browser
4. The default Search & Rescue scenario loads automatically

## Console Layout

| Panel             | Location      | Purpose                              |
|-------------------|---------------|--------------------------------------|
| Asset Panel       | Left          | List of all vehicles with status     |
| Tactical Map      | Center        | 2D view of assets, routes, waypoints |
| System Health     | Top-right     | Mission stats at a glance            |
| Telemetry         | Right         | Raw per-asset data readouts          |
| Command Console   | Bottom-center | Natural-language operator input      |
| Alert Feed        | Bottom-right  | Real-time warnings and events        |

## Issuing Commands

Type commands in the console at the bottom. Examples:

| Command                              | What happens                        |
|--------------------------------------|-------------------------------------|
| "Show status of all assets"          | Returns asset summary (auto)        |
| "What is HAWK-1's battery level?"    | Returns specific telemetry (auto)   |
| "Reroute HAWK-2 to grid sector B4"  | Proposes waypoint change (confirm)  |
| "Return all assets to base"          | Requires operator approval (modal)  |

## Understanding Alerts

- **Blue (info):** Normal operational events
- **Yellow (warning):** Conditions requiring attention (low battery, delays)
- **Red (critical):** Immediate action needed (critical battery, comms loss)

## Connection Status

The top-right indicator shows WebSocket connection state:
- **Green:** Connected, receiving live telemetry
- **Yellow:** Connecting / reconnecting
- **Red:** Disconnected — auto-reconnect in progress
