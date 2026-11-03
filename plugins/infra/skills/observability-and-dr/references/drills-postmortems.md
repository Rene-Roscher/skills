# Restore drills, runbooks and postmortems

Drill format, failure-mode table and game days: `high-availability` (references/drills.md there). This file adds
the evidence each one must leave behind.

## Restore drill record

```text
Drill:        PostgreSQL point-in-time restore from the off-site copy
Date:         [YYYY-MM-DD]
Operator:     [name]              Second person: [name]
Target:       throwaway environment, no production credentials
Started:      [hh:mm]             Service answered correctly: [hh:mm]
Duration:     [minutes]           RTO: [minutes]       Verdict: within / missed
Data check:   row counts of [tables], checksum of [table], known record [id] present
Recovered to: [timestamp]         RPO: [minutes]       Data loss window: [minutes]
Problems:     [list, each with a tracker link]
```

Rules: credentials used are the ones in the break-glass store, not a person's own; the clock starts when the
operator begins, not when the restore command runs; a missed RTO opens an action item.

## Runbook header

```text
Status:       draft | executed
Last run:     [date] by [name], [measured duration]
Mode:         planned | emergency (separate sections when the steps differ)
Preconditions, steps with expected output, verification, rollback, who to inform.
```

A runbook without a last-run date is a draft, whatever its title says. Planned and emergency modes differ when a
step reverses a direction (a mirror that deletes on the target after a flip) or when the planned path drains first.

## Postmortem

Sections: summary, impact (who, how long, measured), timeline in UTC, detection (which alert fired, when, or why
none did), contributing causes, what went well, action items.

Action items: one owner, one due date, one tracker link each; types are prevent, detect, mitigate. Review open
items in a recurring meeting until closed. Language describes systems and decisions, not people's failures.
Replay the alert rules against the incident's series and record when each would have fired.
