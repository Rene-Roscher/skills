# Finding format

One block per finding. Label each claim: verified (you ran or read it in this session), reported (someone or a
tool said so), inferred (follows from evidence you name, not checked directly).

```text
Finding: [one-line title]
Location: [path:line]
Trigger: [input or state that causes it]
Observed: [what happens]          Expected: [what should happen]
Class: [P0 leak | P0 loss or money | P1 | P2 | P3]
Evidence: [verified | reported | inferred] - [test output, event ID, log query]
Fix: [what changed and why it removes the cause]
Regression test: [name]; failed without the fix: [yes, output line]; passes with it: [yes]
Siblings: [search used], [n] checked, [m] found, [fixed or issue links]
Status: [implemented | tested | verified | deployed | live]
Open: [what remains, with links]
```

## Example

From a booking system:

```text
Finding: Cancelling a booking in the last hour before midnight frees the wrong day's slot
Location: src/bookings/cancel.py:42
Trigger: cancellation time between 23:00 and 24:00 local time for venues east of UTC
Observed: the slot of the next day is freed     Expected: the booked slot is freed
Class: P1
Evidence: verified - test_cancel_frees_booked_slot_near_midnight failed with "slot 2026-03-02 freed"
Fix: the slot date is taken from the booking's stored start, not from the current UTC date
Regression test: test_cancel_frees_booked_slot_near_midnight; failed without the fix: yes; passes with it: yes
Siblings: searched "date.today()" and "utcnow().date()" in src/bookings and src/schedules, 7 checked, 1 found
  (src/schedules/reminders.py:88, fixed with its own test)
Status: tested
Open: verify in staging after deploy
```

When it could not be reproduced, replace Trigger, Fix and Regression test with the ranked hypotheses and the
proposed instrumentation.
