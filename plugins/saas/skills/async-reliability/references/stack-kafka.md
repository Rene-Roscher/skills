# Kafka producers and consumers

Load when the project produces to or consumes from Kafka or a Kafka-compatible broker. Facts were read on
2026-11-03 from https://kafka.apache.org/44/design/design/, https://kafka.apache.org/44/operations/monitoring/ and
the franz-go option docs in https://github.com/twmb/franz-go/blob/master/pkg/kgo/config.go. Re-check them at the
client version you run.

## Producer

- franz-go defaults to all in-sync-replica acks (`RequiredAcks` doc: "overriding the default RequireAllISRAcks")
  and idempotent writes (`DisableIdempotentWrite` opts out). Keep both.
- Set `RecordDeliveryTimeout` (roughly `delivery.timeout.ms`). Without it a broker outage leaves produce promises
  pending. franz-go fails all records buffered in the same partition when one times out, to keep ordering gapless.
- Bound the buffer: `MaxBufferedRecords` defaults to 50,000; `MaxBufferedBytes` is unlimited by default.
- On hot paths use `TryProduce`; `ErrMaxBuffered` there means backpressure, not data loss. Report it as its own
  metric.
- Do not attach a request-scoped context to produced records; a cancelled request then fails records that belong
  to other work. Use a background context plus the delivery timeout.
- Key records by entity ID so one entity's messages keep their order in one partition.

## Consumer

- Commit offsets after the effect is durable. Kafka's design doc names the crash between processing and saving
  the position as the at-least-once case, so the sink must deduplicate (unique key, upsert, or a table engine that
  collapses duplicates such as ClickHouse `ReplacingMergeTree`).
- franz-go autocommit commits what was polled before, every 5 s by default. `GreedyAutoCommit` "may result in
  message loss if your application crashes". With manual commits, commit in `OnPartitionsRevoked` or accept
  duplicate processing after a rebalance.
- Poison records: after N handler failures for one record, produce it to a dead-letter topic with headers for the
  source topic, partition, offset, error class and attempt count, then commit past it. A stuck record otherwise
  blocks its whole partition.
- Replay reads the dead-letter topic through the same handler and the same dedup key.
- Keep consumer work bounded: a semaphore or worker pool with a fixed size, and readiness that reports
  backpressure separately from liveness.

## Lag

- Export lag per consumer group and partition: log end offset minus committed offset, or the Java client metric
  `records-lag-max` ("Number of messages the consumer lags behind the producer by", published by the consumer).
- Alert on lag growth over a window and on time since the last commit, not only on an absolute count.
- A new topic or consumer group ships with its lag panel and alert in the same change.

## Tests

- Deliver the same record twice to the handler; one row in the sink.
- Crash after the sink write and before commit (stop the consumer in the test); restart; still one row.
- A record that always fails lands on the dead-letter topic and the partition advances.
