# ADR 007: Store session state in SQLite

## Context

The gateway keeps session state in process memory. A restart drops every active
session, and users must re-authenticate. Deploys happen twice a week, so this is
a recurring interruption.

## Options

1. SQLite file on the local volume. No new infrastructure. Single-writer model
   matches the gateway's single-process design.
2. Redis. Adds a network dependency and a second service to operate for a
   dataset that measures under 10 MB.

## Decision

Use SQLite via `better-sqlite3`. The gateway MUST write session mutations inside
a transaction. The gateway MUST NOT hold a transaction open across an await
point. Validation: restart the gateway under 50 active sessions; all 50 sessions
survive with no re-authentication.

## Consequences

- Session reads add one file I/O per request, measured at 0.1 ms p99 on the
  current volume.
