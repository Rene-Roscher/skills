# web evals

Cases for `web-architecture` and `browser-verification`, run with `claude plugin eval`. Each run is a real model
call on your own credentials.

| Kind | Per skill | Graders | How to run |
|---|---|---|---|
| `trigger` | 10 | the Skill indicator, `min: 1` | `--ablation none --threshold 0.5` |
| `near-miss` | 10 | the Skill indicator, `min: 0`, `max: 0`, `arm: both` | `--ablation none --threshold 0.5` |
| `output` | 2 | result (regex, llm) and process (`tool_used`), plus the Skill indicator | two arms, `--scaffold` |
| `adversarial` | 1 | as output | two arms, `--scaffold` |

Trigger and near-miss cases always run with `--ablation none`: their only grader is the Skill indicator, which
scores zero in the baseline arm by design. Each case description names its split. The first six cases of each
kind per skill are the train split, the last four the validation split. Tune descriptions on train, and judge
a change on validation.

```bash
# trigger and near-miss suite
claude plugin eval ./plugins/web --tag trigger near-miss --ablation none --threshold 0.5

# output and adversarial suite (read the fixture.sh files first: they run outside the sandbox)
claude plugin eval ./plugins/web --tag output adversarial --scaffold --allow-tools Write Edit Bash --threshold 0.8

# one skill while iterating
claude plugin eval ./plugins/web --tag browser-verification --runs 1 --ablation none --scaffold
```

`output-contrast-dark-mode` needs Bash, a working OS sandbox and Playwright browsers on the machine; without
them it measures the honest "not verified in a browser" path. `adversarial-no-browser` grants no Bash on
purpose, so no browser can run.
