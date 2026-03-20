# AEGIS — Data Model

## Entity Relationship Overview

```
missions ──< assets
missions ──< commands
commands ──< audit_log
missions ──< audit_log
assets   ──< audit_log
```

## Tables

### missions
| Column         | Type         | Description                          |
|----------------|--------------|--------------------------------------|
| id             | VARCHAR(64)  | Primary key (e.g., "mission-001")    |
| name           | VARCHAR(256) | Human-readable mission name          |
| mission_type   | VARCHAR(64)  | patrol, search_and_rescue, recon     |
| status         | VARCHAR(32)  | planning, active, completed, aborted |
| asset_count    | INTEGER      | Number of assigned assets            |
| progress_pct   | FLOAT        | 0.0 to 100.0                        |
| created_at     | DATETIME     | UTC timestamp                        |
| started_at     | DATETIME     | When mission went active             |
| completed_at   | DATETIME     | When mission ended                   |
| scenario_config| TEXT         | JSON blob of scenario parameters     |

### assets
| Column       | Type         | Description                           |
|--------------|--------------|---------------------------------------|
| id           | VARCHAR(64)  | Primary key (e.g., "drone-01")        |
| callsign     | VARCHAR(32)  | Operator-facing name (e.g., "HAWK-1") |
| vehicle_type | VARCHAR(32)  | quadrotor, ground_rover, fixed_wing   |
| mission_id   | VARCHAR(64)  | FK → missions.id                      |
| home_x       | FLOAT        | Base X position for RTB               |
| home_y       | FLOAT        | Base Y position for RTB               |
| created_at   | DATETIME     | UTC timestamp                         |

### commands
| Column            | Type         | Description                         |
|-------------------|--------------|-------------------------------------|
| id                | INTEGER      | Auto-increment primary key          |
| mission_id        | VARCHAR(64)  | FK → missions.id                    |
| raw_text          | TEXT         | Exact operator input                |
| interpreted_intent| VARCHAR(256) | AI's interpretation                 |
| risk_level        | VARCHAR(16)  | low, medium, high, blocked          |
| status            | VARCHAR(32)  | pending, approved, executed, failed |
| tools_invoked     | TEXT         | JSON list of tool calls             |
| result_summary    | TEXT         | What happened                       |
| requires_approval | BOOLEAN      | Whether approval was needed         |
| approved_by       | VARCHAR(64)  | Who approved (if applicable)        |
| created_at        | DATETIME     | When command was issued             |
| executed_at       | DATETIME     | When command was executed            |

### audit_log
| Column     | Type         | Description                              |
|------------|--------------|------------------------------------------|
| id         | INTEGER      | Auto-increment primary key               |
| timestamp  | DATETIME     | UTC, millisecond precision               |
| event_type | VARCHAR(64)  | command_issued, alert_raised, etc.       |
| severity   | VARCHAR(16)  | info, warning, critical                  |
| source     | VARCHAR(64)  | operator, agent, policy, simulation      |
| mission_id | VARCHAR(64)  | Context (nullable)                       |
| asset_id   | VARCHAR(64)  | Context (nullable)                       |
| command_id | INTEGER      | Context (nullable)                       |
| message    | TEXT         | Human-readable description               |
| details    | TEXT         | JSON blob with machine-readable context  |

## Design Principles

1. **Audit log is append-only.** No UPDATE or DELETE operations.
2. **Live state lives in memory** (simulation engine), not the database.
3. **Database captures decisions** — what was requested, what was approved, what happened.
4. **Replay is possible** by replaying the audit log in timestamp order.
