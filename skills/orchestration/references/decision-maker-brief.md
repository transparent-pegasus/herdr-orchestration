# Decision Maker Brief Template

Use this template whenever `assignments.decision-making` resolves to
`mode: delegate`: plan resolution after a plan review, reviewer disagreement
adjudication, mid-execution rulings, or final synthesis before the user picks
how to integrate. Separate delegated targets use the Herdr submission below;
a profile self-target in `delegate`, or a subagent fallback, gets this same
contract and no-re-delegation rule in a fresh subagent. When `decision-making`
resolves to `mode: orchestrator`, the active owner decides directly (or via an
optional subagent) with the same authority and output format.

A composer rejects embedded newlines, so the instruction you submit is **one
line of pointers**, and the contract below goes in **its own file**
(`decision-N-brief.md`, in the task's report directory).

## 1. The submitted instruction (one line)

```bash
PANE=w2:p19                                    # idle pane of the resolved decision-maker target
INSTRUCTION="Work in /abs/path/to/worktree — confirm you are there before anything else. Read-only decision task: make no edits and do not mutate the working tree, index, HEAD, or branch state. Read /abs/path/to/decision-N-brief.md first; it holds the plan, review and report inputs, and the exact decision questions. Write your rulings to /abs/path/to/decision-N-report.md and reply with your dispositions, ruling summaries, and that path. Execute this request yourself, directly; re-delegating to other panes or orchestrating is prohibited. End your reply with DECIDE_N immediately followed by _<4-hex>."
target_settings=("Fable 5.2" max)                         # the resolved target's model and effort, if any
COMPOSER_SUBMIT="$SKILL_DIR/scripts/composer-submit.sh"   # using-herdr-sibling-panes
bash "$COMPOSER_SUBMIT" "$PANE" "$INSTRUCTION" "${target_settings[@]}"
herdr pane wait-output "$PANE" --match "DECIDE_N_<4-hex>" --timeout 540000
```

The marker must not appear verbatim in the instruction — describe it as two
fragments the pane concatenates, and keep the whole marker at 16 ASCII
characters or fewer.

## 2. The decision-maker contract (write to the brief file)

```markdown
## Decision-Maker Contract

You are the `decision-maker` for this run. Reviewers advise and implementers
execute; your judgment is final within the run's frozen terms. The active
owner coordinates execution, records your rulings in the run's report, and
dispatches any follow-up work.

### Scope and Read-Only Rules

Your decision pass is read-only on this checkout. Do not edit code, plans, or
reports outside your designated output file, and do not mutate the working
tree, the index, HEAD, or branch state in any way. Never execute `git checkout`,
`git restore`, `git stash`, `git clean`, or `git reset`.

Do all of this judgment yourself. Never hand part of it to another pane, and
never open a pane for a second opinion.

A ruling never rewrites the run's frozen terms: never change
`.herdr-orchestration/config.yaml` or a profile, enable or disable a review
gate, or widen `delegation.pane_scope`.

### Authority and Inputs

The user's requirements are the binding authority — a later requirement wins
where two conflict — the plan is their argument, and your judgment settles
what neither answers. Read:

- **User requirements, in the order given:** [REQUIREMENTS]
- **Plan or design:** [PLAN_PATH]
- **Relevant reports / diff:** [INPUT_PATHS]
- **Open findings / disagreements / question to decide:** [QUESTIONS_OR_FINDINGS]

### What to Decide

- **Plan resolution:** accept, modify, or reject each review finding; resolve
  disagreements between reviewers with reasoning; specify the exact plan
  change or why a finding does not apply.
- **Review findings and disagreements:** grade severity by user-visible
  effect, resolve disagreements between reviewers, and rule on every item a
  reviewer declined to judge.
- **Mid-execution rulings:** decide the smallest change that satisfies the
  requirements, or say that every path forward is a guess.
- **Final synthesis:** evaluate readiness and residual findings before the
  active owner hands the integration options to the user.

### Output Format

Write your complete rulings to the output file named in your instruction, in
one final write:

#### Dispositions
- **[finding or item]** — ACCEPTED | MODIFIED | REJECTED | PARKED
  - **Reasoning:** [grounded in requirement, plan, or code evidence]
  - **Action (if any):** [exact change for the owner or implementer]

#### Rulings
- **Ruling:** [what was decided] — [why] — [what it costs if wrong]

#### Readiness / Next Action
- **Verdict:** [Proceed | Fixes required | Revise plan | Stop and ask the user (only if every path forward is a guess)]
- **Notes for the owner:** [any cross-task constraint to carry]

Then reply in the pane with ONLY a concise summary of your verdicts, the
output file path, and the completion marker.
```

## Placeholders

- **worktree path** — REQUIRED, absolute; the pane does not inherit the orchestrator's cwd
- `[REQUIREMENTS]` — the user's requirements for this task, verbatim, in the order given
- `[PLAN_PATH]` — plan or design path (`None` if there is none)
- `[INPUT_PATHS]` — review reports, implementer reports, and the diff or its path
- `[QUESTIONS_OR_FINDINGS]` — the exact findings, disagreements, or synthesis question to rule on
- **output file + marker** — REQUIRED, unique per decision pass, at most 16 characters, split into fragments in the instruction
