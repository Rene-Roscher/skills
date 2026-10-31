# Worked example: control plane and on-site connectors

A booking system for venues (meeting rooms, courts, studios). Some customers run a local access-control or room
system in their building network that the booking system must read and update. This example shows the boundary
rules applied to that fleet. It is a design sketch, not a product.

## The split

- Control plane (the Laravel app): owns customers, venues, resources, bookings and every decision: conflict
  resolution, which bookings open which doors, cancellation rules, notifications. It compiles product features
  (recurring bookings, buffers, opening hours) into primitive jobs: "set access window W for resource R on
  controller C", "read occupancy of R".
- Connector (a Go binary): runs on a small machine in the customer's building, behind NAT, on hardware the
  customer controls. It executes primitive jobs against the local system and reports raw results: status,
  timings, error class, observed values. It holds no database credentials and takes no decisions.

## Connectivity

1. The connector starts, reads its enrolment token, and registers outbound over TLS. The control plane never
   opens a connection into the building.
2. It pulls its job list with the hash of the list it already has. Equal hash: "not modified". New hash: the full
   list.
3. It spreads periodic jobs over their interval with a deterministic offset per job, so a hundred connectors do
   not hit the control plane in the same second.
4. It heartbeats every N seconds. The response can carry commands: sync now, drain, rotate credentials.
5. A second connector with the same ID evicts the older connection, so a cloned disk image cannot run two
   identities.
6. On planned shutdown it sends a deregister with a short timeout, so an update does not look like an outage.

## Results

- Results go to a durable log or an ingest endpoint in batches. When the control plane is unreachable, the
  connector spools to disk with a byte and count cap, drops the oldest entries and counts the drops.
- The control plane consumes results idempotently by job ID and attempt, applies its rules, and decides what
  customers see.
- Enums on the wire carry only what the connector observes ("ok", "timeout", "refused"). States such as
  "confirmed" or "conflict" exist only in the control plane.

## Secrets

- A job that needs the local system's credentials carries them encrypted with the key dedicated to the
  connector relationship (`encryptString` of a JSON object with `exp`), never with the app's `APP_KEY`.
- The connector decrypts them in memory only, for the job that needs them.
- A credential that is present but cannot be decrypted fails the job with an opaque error. The connector never
  falls back to an unauthenticated call.

## Contract

- `CONTRACT.md` in both repos lists the registration, job list, heartbeat and result endpoints, every field with
  type, unit and nullability, the maximum batch size and payload size, and the deploy order (control plane accepts
  the new field first, connectors start sending it second).
- Golden fixtures produced by the connector's real encoder run in the control plane's tests, and the reverse.
