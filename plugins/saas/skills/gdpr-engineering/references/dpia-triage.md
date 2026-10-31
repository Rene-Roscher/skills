# DSFA (DPIA) triage

Review-ready draft, not legal advice. Scope: EU. Sources: GDPR Art. 35, https://eur-lex.europa.eu/eli/reg/2016/679/oj;
Article 29 Working Party, WP248 rev.01, https://ec.europa.eu/newsroom/article29/items/611236 (verified 2026-10).

## Always a DSFA (Art. 35(3))

- Systematic and extensive evaluation of personal aspects by automated processing, including profiling, on which
  decisions with legal or similarly significant effects are based.
- Large-scale processing of Art. 9 or Art. 10 data.
- Systematic large-scale monitoring of a publicly accessible area.

Your supervisory authority also publishes a list of processing types that always need one (Art. 35(4)). Check
the list of the authority competent for you on the day you triage.

## The nine WP248 criteria

WP248 says that in most cases processing that meets two criteria requires a DSFA.

| Criterion | SaaS example |
|---|---|
| Evaluation or scoring | ranking employees by response time |
| Automated decision with legal or similar effect | automatic account suspension without human review |
| Systematic monitoring | per-user activity timelines visible to managers |
| Sensitive or highly personal data | absence reasons, health, location history |
| Large scale | many tenants' end users in one processing |
| Matching or combining data sets | joining product usage with support and billing data |
| Vulnerable data subjects, including employees | staff of the customer, observed by their employer |
| Innovative technology | new analysis of free text with a language model |
| Prevents exercising a right or using a service | a score that blocks signup |

Example: a team activity dashboard that shows each employee's actions to their manager meets systematic
monitoring and vulnerable data subjects (employees). That is two criteria: plan a DSFA.

## Triage note

Write one note per new processing activity in `privacy/dpia/[activity].md` and link it from the inventory entry:

```markdown
# Triage: [activity]
Date: YYYY-MM-DD. Decided by: [role].
Art. 35(3) case: none | a | b | c
Authority list (Art. 35(4)) checked: [authority, date] - hit: yes | no
WP248 criteria met: [list]
Result: no DSFA | DSFA planned, owner [role], due [date]
Mitigations already in the design: [list]
```
